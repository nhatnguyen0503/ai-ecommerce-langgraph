"""Create a user account from the command line (production has no demo seed).

Usage (inside the backend container):
    python -m app.create_user --email admin@your-shop.fi --role admin
The password is asked interactively and never passed as an argument.
"""

import argparse
import getpass
import sys

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.repositories.user_repository import UserRepository
from app.security import hash_password
from app.services.auth_service import MAX_EMAIL_LENGTH, MAX_PASSWORD_LENGTH

MIN_PASSWORD_LENGTH = 12
ROLES_USER = {"admin", "customer"}


def create_user(db: Session, email: str, password: str, role: str) -> User:
    """Validate input, then create and return the user. Raises ValueError on bad input."""
    email = email.strip().lower()
    if "@" not in email or len(email) > MAX_EMAIL_LENGTH:
        raise ValueError("Invalid email address.")
    if role not in ROLES_USER:
        raise ValueError(f"Role must be one of: {', '.join(sorted(ROLES_USER))}")
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be {MIN_PASSWORD_LENGTH} - {MAX_PASSWORD_LENGTH} characters long."
        )
    if UserRepository(db).get_by_email(email) is not None:
        raise ValueError("A user with this email already exists.")

    user = User(email=email, hashed_password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a user account.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--role", choices=sorted(ROLES_USER), default="customer")
    args = parser.parse_args()

    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Confirm password: "):
        print("Passwords do not match.", file=sys.stderr)
        return 1

    with SessionLocal() as db:
        try:
            user = create_user(db, email=args.email, password=password, role=args.role)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    print(f"Created {user.role} user id = {user.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
