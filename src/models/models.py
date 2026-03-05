import uuid
from datetime import date, time
from sqlalchemy import text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAUUID
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from typing import List

class Base(DeclarativeBase):
    pass


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


class MailVerification(Base):
    __tablename__ = "email_verification"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(nullable=False)
    creation_date: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))
    creation_time: Mapped[time] = mapped_column(Time, server_default=text("CURRENT_TIME"))
    expiration_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiration_time: Mapped[time] = mapped_column(Date, nullable=False)
    was_used: Mapped[bool] = mapped_column(nullable=False, default=False)
