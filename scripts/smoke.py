"""Read-only HTTP smoke test through the frontend proxy after Compose startup."""
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://localhost:5173")
base = parser.parse_args().url.rstrip("/")


def request(path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(base + path, data=json.dumps(data).encode() if data is not None else None, headers=headers)
    with urlopen(req, timeout=15) as response:
        assert response.status == 200
        return json.load(response)


with urlopen(base, timeout=15) as response:
    assert response.status == 200 and b'<div id="root">' in response.read()
for prefix in ("auth", "catalogo", "eventos", "tienda", "proveedores"):
    for endpoint in ("health", "ready"):
        request(f"/api/{prefix}/{endpoint}")
for role in ("admin", "provider", "client"):
    login = request("/api/auth/auth/login", {
        "email": os.getenv(f"SEED_{role.upper()}_EMAIL", f"demo.{role}@subsonic.example.com"),
        "password": os.getenv("SEED_PASSWORD", "DemoSubsonic2026!")})
    assert login["user"]["role"] == role
    token = login["access_token"]
    assert request("/api/auth/users/me", token=token)["id"] == f"demo_{role}"
    if role == "provider":
        assert request("/api/proveedores/providers/me", token=token)["user_id"] == "demo_provider"
for path in ("/api/catalogo/artists", "/api/eventos/events", "/api/eventos/events/demo_event/lineup",
             "/api/eventos/events/demo_event/passes", "/api/tienda/products", "/api/proveedores/external-services"):
    assert request(path), path
print("SPA, 10 health checks, 3 demo accounts, provider profile and demo catalogs verified")
