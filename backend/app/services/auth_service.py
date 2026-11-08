import logging

from app.models import User
from app.repositories.user_repository import UserRepository
from app.security import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)

# Verified against when the email does not exist, so a wrong email takes about
# as long as a wrong password (no user enumeration via response time).
_DUMMY_HASH = hash_password("dummy-password-for-timing")
MAX_EMAIL_LENGTH = 254  # practical maximum for an email address (RFC 5321)
MAX_PASSWORD_LENGTH = 128  # long enough for passphrases, short enough to hash cheaply


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Incorrect email or password")


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def authenticate(self, email: str, password: str) -> User:
        if len(email) > MAX_EMAIL_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
            logger.info("Login rejected: input too long")
            raise InvalidCredentialsError()
        user = self.repo.get_by_email(email.strip().lower())
        if user is None:
            # Verify a dummy hash to make the timing similar to a real user.
            verify_password(password, _DUMMY_HASH)
            logger.info("Login failed: unknown account")
            raise InvalidCredentialsError()
        if not verify_password(password, user.hashed_password) or not user.is_active:
            logger.info("Login failed for user_id=%s", user.id)
            raise InvalidCredentialsError()
        logger.info("Login successful for user_id=%s", user.id)
        return user

    def login(self, email: str, password: str) -> str:
        user = self.authenticate(email, password)
        return create_access_token(subject=str(user.id), role=user.role)
