import pytest

from app.models import User
from app.security import decode_access_token, hash_password
from app.dependencies import require_admin
from app.security import create_access_token
from fastapi import HTTPException

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


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_me_return_current_user(client, user):
    token = create_access_token(subject=str(user.id), role=user.role)
    response = client.get("/auth/me", headers=_bearer(token))
    assert response.status_code == 200
    assert response.json() == {"id": user.id, "email": "aino@example.fi", "role": "customer"}


def test_me_without_token_is_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("token", [
    "not-a-jwt",
    create_access_token(subject="abc", role="admin"), # sub is not an int
    create_access_token(subject="999999", role="admin"), # user does not exist
])

def test_me_with_bad_token_is_401(client, user, token):
    response = client.get("/auth/me", headers=_bearer(token))
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_me_for_deactivated_user_is_401(client, db, user):
    token = create_access_token(subject=str(user.id), role=user.role)
    user.is_active = False
    db.commit()
    assert client.get("/auth/me", headers=_bearer(token)).status_code == 401


def test_me_response_never_contains_password_hash(client, user):
    token = create_access_token(subject=str(user.id), role=user.role)
    assert "hashed_password" not in client.get("/auth/me", headers=_bearer(token)).json()

def test_require_admin_reject_customer(user):
    with pytest.raises(HTTPException) as exc_info:
        require_admin(user)
    assert exc_info.value.status_code == 403

def test_require_admin_allows_admin(user):
    user.role = "admin"
    assert require_admin(user) is user
