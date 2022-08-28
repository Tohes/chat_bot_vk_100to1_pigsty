from dataclasses import dataclass
from hashlib import sha256
from typing import Optional
from sqlalchemy.orm import declarative_base
from app.store.database.sqlalchemy_base import db

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    NUMERIC,
    PrimaryKeyConstraint,
    TIMESTAMP,
    Text,
    VARCHAR,
    String
)


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])


class AdminModel(db):
    __tablename__ = "admins"
    id = Column(Integer, primary_key = True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    __table_args__ = {'extend_existing': True}
