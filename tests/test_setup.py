"""Integration tests. Requires five dedicated PostgreSQL *_seed_test databases."""
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("service,db", [
    ("auth", "auth"), ("catalog", "catalog"), ("event", "events"),
    ("commerce", "commerce"), ("provider", "providers"),
])
def test_initialization_seed_and_startup(service, db):
    env = dict(os.environ, DB_NAME=f"subsonic_{db}_seed_test",
               PYTHONPATH=str(ROOT / f"{service}-service/generated/src"))
    subprocess.run([sys.executable, str(ROOT / "tests/setup_worker.py"), service],
                   env=env, check=True)
