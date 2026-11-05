import pytest

from app.models import User
from app.security import decode_access_token, hash_password

PASSWORD = "test_password"


@pytest.fixture
def user(db):
    u = User(
        email="aino@example.fi",
        hashed_password=hash_password(PASSWORD),
        role="customer",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _login(client, username: str, password: str):
    return client.post("/auth/login", data={"username": username, "password": password})


def test_login_returns_bearer_token_for_user(client, user):
    response = _login(client, "aino@example.fi", PASSWORD)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == str(user.id)
    assert payload["role"] == "customer"


def test_login_email_is_case_insensitive(client, user):
    assert _login(client, "AINO@EXAMPLE.FI", PASSWORD).status_code == 200


@pytest.mark.parametrize(
    "username,password",
    [
        ("aino@example.fi", "wrong-password"),  # wrong password
        ("nobody@EXAMPLE.FI", PASSWORD),  # non-existent user
    ]
)
def test_bad_credentials_give_same_401(client, user, username, password):
    response = _login(client, username, password)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.headers["www-authenticate"] == "Bearer"


def test_inactive_user_cannot_login(client, db, user):
    user.is_active = False
    db.commit()
    assert _login(client, "aino@example.fi", PASSWORD).status_code == 401


def test_login_requires_form_fields(client):
    assert client.post("/auth/login", data={}).status_code == 422
