# app/models.py
from __future__ import annotations

import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID  # ← тип UUID для Postgres

Base = declarative_base()


# ────────────────────────────────────
#            USERS
# ────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: uuid.UUID | Column = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)

    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # связь 1-N → Book
    books = relationship("Book", back_populates="user", cascade="all, delete-orphan")


# ────────────────────────────────────
#            BOOKS
# ────────────────────────────────────
class Book(Base):
    __tablename__ = "books"

    id: uuid.UUID | Column = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    run_id = Column(String, nullable=False, index=True)  # ID из Apify
    title = Column(String, nullable=False)

    # Информация профиля Instagram
    profile_username = Column(String)
    profile_full_name = Column(String)
    profile_followers = Column(Integer)
    profile_posts_count = Column(Integer)

    # Файлы
    html_path = Column(String)
    pdf_path = Column(String)
    images_path = Column(String)

    # Статус
    is_completed = Column(Boolean, default=False)
    has_html = Column(Boolean, default=False)
    has_pdf = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Доп. данные (JSON-строкой)
    book_metadata = Column(Text)

    # связь N-1 → User
    user = relationship("User", back_populates="books")


# ────────────────────────────────────
#       PROCESSING SESSIONS
# ────────────────────────────────────
class ProcessingSession(Base):
    """Отслеживание прогресса Apify-запуска"""

    __tablename__ = "processing_sessions"

    id: uuid.UUID | Column = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    instagram_url = Column(String, nullable=False)

    # Статус
    status = Column(String, default="started")  # started | scraping | building | ...
    current_stage = Column(String)
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # связь N-1 → User
    user = relationship("User")
