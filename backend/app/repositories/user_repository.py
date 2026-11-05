from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by id"""
        return self.session.get(User, user_id)
