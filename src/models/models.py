import uuid
from datetime import date, time

from pydantic_core.core_schema import nullable_schema
from sqlalchemy import text, Date, Time, ForeignKey, DateTime, null
from sqlalchemy.dialects.postgresql import UUID as SQLAUUID
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from typing import List

class Base(DeclarativeBase):
    pass


class AllUsers(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default="user")


class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    date: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))
    time: Mapped[time] = mapped_column(Time, server_default=text("CURRENT_TIME"))
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="active")
    answers: Mapped[List["Answers"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan"
    )


class Answers(Base):
    __tablename__ = "answers"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    date: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))
    time: Mapped[time] = mapped_column(Time, server_default=text("CURRENT_TIME"))
    message: Mapped[str] = mapped_column(nullable=False, default="")
    question_id: Mapped[uuid.UUID] = mapped_column(
        SQLAUUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),  # Важно!
        nullable=False
    )
    question: Mapped["Questions"] = relationship(
        back_populates="answers"
    )


class EmailVerification(Base):
    __tablename__ = "email_verification"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    creation: Mapped[date] = mapped_column(DateTime, nullable=False)
    expiration: Mapped[time] = mapped_column(DateTime, nullable=False)
    was_used: Mapped[bool] = mapped_column(nullable=False, default=False)
