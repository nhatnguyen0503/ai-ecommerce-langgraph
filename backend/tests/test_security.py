from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

# --- passwords ---


def test_hash_is_not_plain_text():
    assert hash_password("user-pass") != "user-pass"


def test_verify_password_accepts_correct_and_rejects_wrong():
    hashed = hash_password("user-pass")
    assert verify_password("user-pass", hashed) is True
    assert verify_password("wrong-pass", hashed) is False


def test_same_password_give_different_hashes():
    # different salts should produce different hashes for the same password
    hash1 = hash_password("user-pass")
    hash2 = hash_password("user-pass")
    assert hash1 != hash2  # different salts


# --- tokens ---
def test_token_roundtrip_contains_sub_and_role():
    token = create_access_token(subject="user-pass", role="admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-pass"
    assert payload["role"] == "admin"


def test_expired_token_is_rejected():
    two_hours_ago = datetime.now(UTC) - timedelta(hours=2)
    token = create_access_token(
        subject="user-pass", role="admin", expires_delta=timedelta(minutes=30), now=two_hours_ago
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_tampered_payload_is_rejected():
    token = create_access_token(subject="user-pass", role="customer")
    header, payload, signature = token.split(".")
    forged = jwt.encode(
        {"sub": "tampered-user", "role": "admin", "exp": 99999999},
        "attacked_key" + "x" * 32,
        algorithm="HS256",
    )
    _, forged_payload, _ = forged.split(".")
    tempered = f"{header}.{forged_payload}.{signature}"  # admin payload with original signature

    with pytest.raises(InvalidTokenError):
        decode_access_token(tempered)


def test_token_signed_with_other_key_is_rejected():
    forged = jwt.encode(
        {"sub": "user-pass", "role": "admin", "exp": 99999999}, "x" * 32, algorithm="HS256"
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(forged)


def test_unsigned_alg_none_token_is_rejected():
    forged = jwt.encode({"sub": "42", "role": "admin", "exp": 9999999999}, None, algorithm="none")
    with pytest.raises(InvalidTokenError):
        decode_access_token(forged)
