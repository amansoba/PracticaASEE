"""Read-only HTTP smoke test through the frontend proxy after Compose startup."""

import argparse
import json
import os
import socket
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://localhost:5173")
base = parser.parse_args().url.rstrip("/")

passed = 0
failed = []


def request(path, data=None, token=None):
    """Perform an HTTP request and return decoded JSON without logging tokens."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = json.dumps(data).encode() if data is not None else None
    req = Request(base + path, data=payload, headers=headers)
    try:
        with urlopen(req, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
            body = response.read()
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise RuntimeError("timeout") from exc
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"connection/DNS error: {reason}") from exc

    if not body:
        raise RuntimeError("empty response body")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("invalid JSON response") from exc


def check(name, function):
    global passed
    try:
        function()
    except Exception as exc:  # noqa: BLE001 - report every smoke failure
        failed.append((name, str(exc)))
        print(f"[FAIL] {name}: {exc}")
    else:
        passed += 1
        print(f"[ OK ] {name}")


def check_frontend():
    try:
        with urlopen(base, timeout=15) as response:
            body = response.read()
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise RuntimeError("timeout") from exc
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"connection/DNS error: {reason}") from exc
    if b"<div id=\"root\">" not in body:
        raise RuntimeError("SPA root element not found")


def check_health(prefix, endpoint):
    response = request(f"/api/{prefix}/{endpoint}")
    if not isinstance(response, dict) or response.get("status") not in {"ok", "ready"}:
        raise RuntimeError(f"unexpected response: {response!r}")


def check_login(role):
    login = request("/api/auth/auth/login", {
        "email": os.getenv(
            f"SEED_{role.upper()}_EMAIL",
            f"demo.{role}@subsonic.example.com",
        ),
        "password": os.getenv("SEED_PASSWORD", "DemoSubsonic2026!"),
    })
    if login.get("user", {}).get("role") != role:
        raise RuntimeError("unexpected role in login response")
    token = login.get("access_token")
    if not token:
        raise RuntimeError("login response did not contain an access token")
    profile = request("/api/auth/users/me", token=token)
    if profile.get("id") != f"demo_{role}":
        raise RuntimeError("unexpected authenticated profile")
    if role == "provider":
        provider = request("/api/proveedores/providers/me", token=token)
        if provider.get("user_id") != "demo_provider":
            raise RuntimeError("unexpected provider profile")
    return token


def main():
    check("frontend/Nginx SPA", check_frontend)

    prefixes = {
        "auth": "auth",
        "catalog": "catalogo",
        "event": "eventos",
        "commerce": "tienda",
        "provider": "proveedores",
    }
    for service, prefix in prefixes.items():
        for endpoint in ("health", "ready"):
            check(
                f"{service} /{endpoint} via frontend",
                lambda prefix=prefix, endpoint=endpoint: check_health(prefix, endpoint),
            )

    tokens = {}
    for role in ("admin", "provider", "client"):
        check(
            f"auth login and profile ({role})",
            lambda role=role: tokens.__setitem__(role, check_login(role)),
        )

    # This GET is read-only and requires Commerce to call Auth through
    # GET /users/me before returning the user's order history.
    def check_commerce_auth():
        token = tokens.get("client")
        if not token:
            raise RuntimeError("client token unavailable because login failed")
        response = request("/api/tienda/orders/user/demo_client", token=token)
        if not isinstance(response, list):
            raise RuntimeError("expected a JSON list of orders")

    check("commerce -> auth protected GET", check_commerce_auth)

    data_checks = {
        "catalog artists": "/api/catalogo/artists",
        "event events": "/api/eventos/events",
        "event lineup": "/api/eventos/events/demo_event/lineup",
        "event passes": "/api/eventos/events/demo_event/passes",
        "commerce products": "/api/tienda/products",
        "provider external services": "/api/proveedores/external-services",
    }
    for name, path in data_checks.items():
        check(
            name,
            lambda path=path: _require_nonempty_json_list(request(path)),
        )

    print(f"\nSmoke summary: {passed} passed, {len(failed)} failed")
    if failed:
        print("Failed checks:")
        for name, error in failed:
            print(f"- {name}: {error}")
        return 1
    print("Overall result: PASS")
    return 0


def _require_nonempty_json_list(value):
    if not isinstance(value, list) or not value:
        raise RuntimeError("expected a non-empty JSON list")


if __name__ == "__main__":
    sys.exit(main())
