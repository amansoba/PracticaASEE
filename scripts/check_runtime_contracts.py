"""Check canonical contracts against FastAPI routes without connecting to a DB."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ("auth", "catalog", "event", "commerce", "provider")
METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def check(service):
    sys.path.insert(0, str(ROOT / f"{service}-service/generated/src"))
    from openapi_server.main import app
    spec = yaml.safe_load((ROOT / f"{service}-service/openapi.yaml").read_text(encoding="utf-8"))
    runtime = app.openapi()
    def operations(document):
        return {(path, method): operation for path, item in document["paths"].items()
                for method, operation in item.items() if method in METHODS}
    canonical, actual = operations(spec), operations(runtime)
    assert canonical.keys() == actual.keys(), (service, canonical.keys() ^ actual.keys())
    for key, operation in actual.items():
        assert set(operation["responses"]) <= set(canonical[key]["responses"]), (service, key, "missing HTTP responses")
    schemas = runtime.get("components", {}).get("schemas", {})
    for name, schema in spec["components"]["schemas"].items():
        if name in schemas:
            assert schema.get("properties", {}).keys() == schemas[name].get("properties", {}).keys(), (service, name)
            assert set(schema.get("required", [])) == set(schemas[name].get("required", [])), (service, name, "required fields")
            for field, actual_field in schemas[name].get("properties", {}).items():
                nullable = any(item.get("type") == "null" for item in actual_field.get("anyOf", []))
                assert bool(schema["properties"][field].get("nullable")) == nullable, (service, name, field, "nullable")
    print(f"{service}: {len(actual)} routes and shared schema fields match runtime")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", choices=SERVICES)
    args = parser.parse_args()
    if args.service:
        check(args.service)
    else:
        for service in SERVICES:
            subprocess.run([sys.executable, __file__, "--service", service], check=True, env={
                **os.environ, "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "example-contract-validation-only-32-characters")})
