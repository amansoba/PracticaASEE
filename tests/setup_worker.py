"""Separate interpreter for each service, to avoid openapi_server collisions."""
from pathlib import Path
import os
import subprocess
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import OperationalError

from openapi_server.database import engine, SessionLocal
from openapi_server.db_models import Base
from openapi_server.main import app

ROOT = Path(__file__).resolve().parents[1]
service = sys.argv[1]
assert engine.url.database.endswith("_seed_test"), "Dedicated seed DB required"
# Deliberately do not drop data: this test also supports repeated runs.
with TestClient(app):
    assert set(Base.metadata.tables) <= set(inspect(engine).get_table_names())
if service == "auth":
    assert {"users", "revoked_tokens", "password_resets", "user_token_invalidations"} <= set(Base.metadata.tables)


def counts():
    with engine.connect() as connection:
        return {t.name: connection.scalar(select(func.count()).select_from(t))
                for t in Base.metadata.sorted_tables}


command = [sys.executable, str(ROOT / "scripts/seed.py"), "--service", service]
subprocess.run(command, check=True)
before = counts()
assert all(n > 0 for name, n in before.items() if name not in {
    "revoked_tokens", "password_resets", "user_token_invalidations", "orders", "order_items"})
subprocess.run(command, check=True)
assert counts() == before, "Seed duplicated rows"
with TestClient(app) as client:
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    with patch("openapi_server.health.engine.connect", side_effect=OperationalError("test", {}, Exception("offline"))):
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 503
    if service == "auth":
        response = client.post("/auth/login", json={
            "email": os.getenv("SEED_ADMIN_EMAIL", "demo.admin@subsonic.example.com"),
            "password": os.getenv("SEED_PASSWORD", "DemoSubsonic2026!")})
        assert response.status_code == 200, response.text
        assert response.json()["user"]["role"] == "admin"
    else:
        path = {"catalog": "/artists", "event": "/events", "commerce": "/products",
                "provider": "/external-services"}[service]
        response = client.get(path)
        assert response.status_code == 200, response.text
        assert response.json()
print(service, "startup + repeated seed + API smoke verified", before)
