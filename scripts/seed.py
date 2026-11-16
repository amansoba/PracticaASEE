"""Insert demo data into existing models, once per stable demo ID.

Run each service in its own process: they share the openapi_server package name.
Existing rows (including passwords and stock) are never updated by this seed.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from datetime import date, datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ("auth", "catalog", "event", "commerce", "provider")


def seed(service):
    from dotenv import load_dotenv
    directory = ROOT / f"{service}-service/generated"
    load_dotenv(directory / ".env")
    sys.path.insert(0, str(directory / "src"))
    from openapi_server.database import SessionLocal, engine
    from openapi_server import db_models as m
    if service == "auth":
        import openapi_server.auth_flows  # register all authentication tables
        import openapi_server.login_rate_limit  # integration adds login attempt persistence
    m.Base.metadata.create_all(engine)
    with SessionLocal.begin() as db:
        def add(model, key, **values):
            row = db.get(model, key)
            if row is None:
                row = model(id=key, **values)
                db.add(row)
                db.flush()
            return row

        if service == "auth":
            from openapi_server.auth_security import cifrar_password
            from sqlalchemy import select
            password = os.getenv("SEED_PASSWORD", "DemoSubsonic2026!")
            if len(password) < 8:
                raise ValueError("SEED_PASSWORD must have at least 8 characters")
            for role in ("admin", "provider", "client"):
                email = os.getenv(f"SEED_{role.upper()}_EMAIL", f"demo.{role}@subsonic.example.com").strip().lower()
                existing = db.scalar(select(m.UserDB).where(m.UserDB.email == email))
                if existing is not None and existing.id != f"demo_{role}":
                    raise ValueError(f"Demo email already belongs to another account: {email}")
                add(m.UserDB, f"demo_{role}", name=f"Demo {role}", email=email,
                    password_hash=cifrar_password(password), role=role)
        elif service == "catalog":
            for index, (name, genre) in enumerate((("Demo Pulse", "Electronic"), ("Demo Waves", "Indie")), 1):
                add(m.ArtistDB, f"demo_artist_{index}", name=name, genre=genre)
                add(m.SongDB, f"demo_song_{index}", artist_id=f"demo_artist_{index}", title=f"Demo Track {index}")
        elif service == "event":
            add(m.EventDB, "demo_event", name="Subsonic Demo Festival", start_date=date(2027, 7, 16),
                end_date=date(2027, 7, 17), venue="Demo Arena", location_city="Caceres")
            for index in (1, 2):
                add(m.ScheduleEntryDB, f"demo_schedule_{index}", event_id="demo_event",
                    artist_id=f"demo_artist_{index}", artist_name=("Demo Pulse", "Demo Waves")[index-1],
                    stage="Main", start_time=datetime(2027, 7, 16, 18+index, tzinfo=timezone.utc),
                    end_time=datetime(2027, 7, 16, 19+index, tzinfo=timezone.utc))
            # One issued ticket, so 99 of the 100 passes remain available.
            add(m.PassConfigDB, "demo_pass", event_id="demo_event", type_name="General Demo",
                price=50, capacity=100, available_tickets=99, benefits=[])
            add(m.TicketDB, "demo_ticket", event_id="demo_event", pass_id="demo_pass",
                user_id="demo_client", qr_code="DEMO-NOT-VALID-AT-REAL-EVENTS", status="valid",
                purchased_at=datetime(2026, 11, 16, tzinfo=timezone.utc))
        elif service == "commerce":
            from sqlalchemy import select
            for index, name in enumerate(("Demo T-shirt", "Demo Hoodie"), 1):
                product = add(m.ProductDB, f"demo_product_{index}", name=name, category="ropa", price=20*index, images=[])
                for size in ("S", "M", "L"):
                    variant = db.scalar(select(m.ProductVariantDB).where(
                        m.ProductVariantDB.product_id == product.id, m.ProductVariantDB.size == size))
                    if variant is None:
                        db.add(m.ProductVariantDB(product_id=product.id, size=size, stock=25))
        elif service == "provider":
            add(m.ProviderDB, "demo_provider_company", user_id="demo_provider", company_name="Demo Sound SL",
                cif_nif="DEMO-B00000000", service_category="sonido",
                contact_email=os.getenv("SEED_PROVIDER_EMAIL", "demo.provider@subsonic.example.com"))
            add(m.ExternalServiceDB, "demo_service", name="Demo sound system", description="Demo equipment")
            add(m.SpaceDB, "demo_space", event_id="demo_event", name="Demo stage area",
                dimensions="10x10m", base_price=300, is_available=True)
            add(m.SpaceProposalDB, "demo_proposal", space_id="demo_space", provider_id="demo_provider_company",
                event_id="demo_event", budget_proposal=350, setup_date=date(2027, 7, 15), status="pending")
    print(f"{service}: schema and demo data ready")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", choices=SERVICES)
    args = parser.parse_args()
    if args.service:
        seed(args.service)
    else:
        for service in SERVICES:
            subprocess.run([sys.executable, __file__, "--service", service], check=True)


if __name__ == "__main__":
    main()
