from datetime import timedelta

from src.core.security import create_token, decode_token, hash_password, verify_password


def test_password_hash_round_trip():
    password_hash = hash_password("StrongPass123")
    assert password_hash != "StrongPass123"
    assert verify_password("StrongPass123", password_hash)


def test_jwt_round_trip():
    token = create_token("42", "access", timedelta(minutes=5), {"role": "trader"})
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["role"] == "trader"

