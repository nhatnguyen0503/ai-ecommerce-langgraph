import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User


def _user(email: str = "a@example.fi", **kw) -> User:
    return User(email=email, hashed_password="not-a-real-hash", **kw)


def test_new_user_defaults_to_customer_and_activate(empty_db):
    user = _user()
    empty_db.add(user)
    empty_db.commit()
    empty_db.refresh(user)  # reload server-side defaults from the DB
    assert user.role == "customer"
    assert user.is_active is True


def test_email_must_be_unique(empty_db):
    empty_db.add(_user(email="a@example.fi"))
    empty_db.commit()
    empty_db.add(_user(email="a@example.fi"))
    with pytest.raises(IntegrityError):
        empty_db.commit()


def test_role_must_be_customer_or_admin(empty_db):
    empty_db.add(_user(role="invalid"))
    with pytest.raises(IntegrityError):
        empty_db.commit()
