from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связь с книгами
    books = relationship("Book", back_populates="user", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    run_id = Column(String, nullable=False, index=True)  # ID из Apify
    title = Column(String, nullable=False)
    
    # Информация о профиле из Instagram
    profile_username = Column(String, nullable=True)
    profile_full_name = Column(String, nullable=True)
    profile_followers = Column(Integer, nullable=True)
    profile_posts_count = Column(Integer, nullable=True)
    
    # Файлы
    html_path = Column(String, nullable=True)  # Путь к HTML файлу
    pdf_path = Column(String, nullable=True)   # Путь к PDF файлу
    images_path = Column(String, nullable=True) # Путь к папке с изображениями
    
    # Статус
    is_completed = Column(Boolean, default=False)
    has_html = Column(Boolean, default=False)
    has_pdf = Column(Boolean, default=False)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Дополнительные данные в JSON формате (renamed from 'metadata' to avoid conflict)
    book_metadata = Column(Text, nullable=True)  # JSON строка с дополнительными данными
    
    # Связь с пользователем
    user = relationship("User", back_populates="books")

class ProcessingSession(Base):
    """Сессии обработки для отслеживания прогресса"""
    __tablename__ = "processing_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    instagram_url = Column(String, nullable=False)
    
    # Статус обработки
    status = Column(String, default="started")  # started, scraping, building, completed, failed
    current_stage = Column(String, nullable=True)
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Временные метки
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связь с пользователем
    user = relationship("User") 