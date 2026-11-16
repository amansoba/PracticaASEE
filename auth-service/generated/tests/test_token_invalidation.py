"""Preserve the conservative JWT invalidation boundary at password reset."""
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from openapi_server import auth_flows


@pytest.mark.parametrize("issued,cutoff,expected", [
    (1699999999, 1700000000, True),
    (1700000000, 1700000000, True),
    (1700000000, 1700000000.5, True),
    (1700000001, 1700000000.5, False),
])
def test_token_invalidation_boundary(monkeypatch, issued, cutoff, expected):
    record = SimpleNamespace(invalid_before=datetime.fromtimestamp(cutoff, tz=timezone.utc))

    @contextmanager
    def session():
        yield SimpleNamespace(get=lambda model, key: record)

    monkeypatch.setattr(auth_flows, "SessionLocal", session)
    assert auth_flows.token_usuario_invalidado({"sub": "demo_client", "iat": issued}) is expected


def test_token_without_invalidation_record(monkeypatch):
    @contextmanager
    def session():
        yield SimpleNamespace(get=lambda model, key: None)

    monkeypatch.setattr(auth_flows, "SessionLocal", session)
    assert not auth_flows.token_usuario_invalidado({"sub": "demo_client", "iat": 1700000000})
