"""
Module to defined all database tables
"""

from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
    """
    Base class
    """
    pass

db_connector = SQLAlchemy(model_class=Base)

class User(db_connector.Model):
    """
    ORM class for User table
    """
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)

    # allow for session to be nullable since a user can exist without having a session if they are fully logged out
    session: Mapped['Session'] = relationship(back_populates="user")

    def __repr__(self):
        return f"user_id= {self.user_id}, username= {self.username}, password= {self.password}"

    def __eq__(self, other):
        if isinstance(other, User):
            return self.user_id == other.user_id and self.username == other.username and self.password == other.password
        return False

class Session(db_connector.Model):
    """
    ORM class for sessions
    """
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    user: Mapped['User'] = relationship(back_populates="session")
