from enum import Enum

from datetime import datetime, date

from sqlalchemy import (
    Integer,
    String,
    func,
    ForeignKey,
    Boolean,
    Column,
    Enum as SqlEnum,
)
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import DateTime, Date


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(backref="contacts")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "is_confirmed": self.is_confirmed,
            "created_at": self.created_at.isoformat(),
            "avatar": self.avatar,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            email=data.get("email"),
            hashed_password=data.get("hashed_password"),
            avatar=data.get("avatar"),
            created_at=datetime.fromisoformat(data.get("created_at")),
            is_confirmed=data.get("is_confirmed"),
            role=data.get("role"),
        )
