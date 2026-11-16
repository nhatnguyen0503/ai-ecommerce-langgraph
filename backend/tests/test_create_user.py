import pytest

from app.create_user import create_user
from app.security import verify_password

GOOD_PASSWORD = "correct-horse-battery"


def test_creates_user_with_normalized_email_and_hashed_password(empty_db):
    user = create_user(empty_db, "  Admin@Demo.FI ", password=GOOD_PASSWORD, role="admin")

    assert user.id is not None
    assert user.email == "admin@demo.fi"
    assert user.role == "admin"
    assert user.hashed_password != GOOD_PASSWORD
    assert verify_password(GOOD_PASSWORD, user.hashed_password)


def test_rejects_duplicate_email(empty_db):
    create_user(empty_db, "aino@example.fi", password=GOOD_PASSWORD, role="customer")

    with pytest.raises(ValueError, match="already exists"):
        create_user(empty_db, "AINO@example.fi", password=GOOD_PASSWORD, role="customer")


def test_rejects_short_password(empty_db):
    with pytest.raises(ValueError, match="characters"):
        create_user(empty_db, "aino@example.fi", "short", "customer")


def test_rejects_unknown_role(empty_db):
    with pytest.raises(ValueError, match="Role"):
        create_user(empty_db, "aino@example.fi", password=GOOD_PASSWORD, role="superuser")


def test_rejects_invalid_email(empty_db):
    with pytest.raises(ValueError, match="email"):
        create_user(empty_db, "not-an-email", password=GOOD_PASSWORD, role="customer")


def test_error_message_never_contains_the_password(empty_db):
    secret = "tiny-secret"  # 11 chars: too short, so an error is raised
    with pytest.raises(ValueError) as exc:
        create_user(empty_db, "aino@example.fi", password=secret, role="customer")

    assert secret not in str(exc.value)
