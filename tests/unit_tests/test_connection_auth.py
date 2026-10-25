"""Tests for access-token expiration handling."""

import base64
import json
import os
import time
from datetime import datetime, timezone

import pytest

from teslajsonpy import connection as connection_module
from teslajsonpy.connection import Connection


def _jwt(expiry: int) -> str:
    payload = base64.urlsafe_b64encode(
        json.dumps({"exp": expiry}).encode()
    ).decode().rstrip("=")
    return f"header.{payload}.signature"


@pytest.mark.parametrize(
    "utc_now",
    [
        1792889824,  # 2026-10-25 00:57:04 UTC, BST before the fall-back
        1774747800,  # 2026-03-29 01:30:00 UTC, after the spring-forward
    ],
    ids=["dst-fall-back", "dst-spring-forward"],
)
def test_expiration_uses_utc_epoch_during_dst(monkeypatch, utc_now):
    old_timezone = os.environ.get("TZ")
    monkeypatch.setenv("TZ", "Europe/London")
    time.tzset()
    monkeypatch.setattr(time, "time", lambda: utc_now)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls.fromtimestamp(utc_now + 3600, timezone.utc).replace(
                tzinfo=None
            )

    monkeypatch.setattr(connection_module.datetime, "datetime", FrozenDateTime)
    try:
        connection = Connection(websession=None)
        connection._Connection__sethead("opaque-access-token", expires_in=3600)
        assert connection.expiration == utc_now + 3600
    finally:
        if old_timezone is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old_timezone
        time.tzset()


@pytest.mark.parametrize(
    ("token", "supplied_expiry", "expected_expiry"),
    [
        (_jwt(2000), 3000, 2000),
        (_jwt(900), 3000, 900),
        ("opaque-access-token", 3000, 3000),
        ("header.%%%.signature", 3000, 3000),
        ("header.e30.signature", 3000, 3000),
    ],
    ids=[
        "future-jwt-expiry-clamps-supplied-expiry",
        "expired-jwt-expiry-clamps-supplied-expiry",
        "opaque-token-keeps-supplied-expiry",
        "malformed-token-keeps-supplied-expiry",
        "jwt-without-exp-keeps-supplied-expiry",
    ],
)
def test_jwt_expiry_clamps_only_when_valid(
    monkeypatch, token, supplied_expiry, expected_expiry
):
    monkeypatch.setattr(time, "time", lambda: 1000)
    connection = Connection(websession=None)
    connection._Connection__sethead(token, expiration=supplied_expiry)
    assert connection.expiration == expected_expiry
