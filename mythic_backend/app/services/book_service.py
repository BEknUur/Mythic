from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from ..models import User, Book
from .user_service import UserService
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import shutil
import os

class BookService:
    
    @staticmethod
    async def create_book(
        db: AsyncSession,
        clerk_user_id: str,
        run_id: str,
        title: str,
        profile_data: Optional[Dict[str, Any]] = None,
        html_path: Optional[str] = None,
        pdf_path: Optional[str] = None,
        images_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Book:
        """Создать новую книгу"""
        user = await UserService.get_or_create_user(db, clerk_user_id)
        
        book = Book(
            user_id=user.id,
            run_id=run_id,
            title=title,
            html_path=html_path,
            pdf_path=pdf_path,
            images_path=images_path,
            has_html=html_path is not None and Path(html_path).exists(),
            has_pdf=pdf_path is not None and Path(pdf_path).exists(),
            is_completed=True,
            book_metadata=json.dumps(metadata) if metadata else None
        )
        
        # Добавляем данные профиля если есть
        if profile_data:
            book.profile_username = profile_data.get("username")
            book.profile_full_name = profile_data.get("fullName")
            book.profile_followers = profile_data.get("followersCount")
            book.profile_posts_count = profile_data.get("postsCount")
        
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book
    
    @staticmethod
    async def get_user_books(db: AsyncSession, clerk_user_id: str) -> List[Book]:
        """Получить все книги пользователя"""
        return await UserService.get_user_books(db, clerk_user_id)
    
    @staticmethod
    async def get_book_by_id(db: AsyncSession, book_id: str, clerk_user_id: str) -> Optional[Book]:
        """Получить книгу по ID (только если принадлежит пользователю)"""
        stmt = (
            select(Book)
            .join(User)
            .where(Book.id == book_id)
            .where(User.clerk_user_id == clerk_user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_book_by_run_id(db: AsyncSession, run_id: str, clerk_user_id: str) -> Optional[Book]:
        """Получить книгу по run_id (только если принадлежит пользователю)"""
        stmt = (
            select(Book)
            .join(User)
            .where(Book.run_id == run_id)
            .where(User.clerk_user_id == clerk_user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_book_files(
        db: AsyncSession,
        book_id: str,
        html_path: Optional[str] = None,
        pdf_path: Optional[str] = None,
        images_path: Optional[str] = None
    ) -> Optional[Book]:
        """Обновить пути к файлам книги"""
        stmt = select(Book).where(Book.id == book_id)
        result = await db.execute(stmt)
        book = result.scalar_one_or_none()
        
        if not book:
            return None
        
        if html_path is not None:
            book.html_path = html_path
            book.has_html = Path(html_path).exists()
        
        if pdf_path is not None:
            book.pdf_path = pdf_path
            book.has_pdf = Path(pdf_path).exists()
        
        if images_path is not None:
            book.images_path = images_path
        
        book.is_completed = book.has_html or book.has_pdf
        
        await db.commit()
        await db.refresh(book)
        return book
    
    @staticmethod
    async def delete_book(db: AsyncSession, book_id: str, clerk_user_id: str) -> bool:
        """Удалить книгу (только если принадлежит пользователю)"""
        # Сначала получаем книгу с проверкой владельца
        book = await BookService.get_book_by_id(db, book_id, clerk_user_id)
        if not book:
            return False
        
        # Удаляем файлы с диска
        try:
            if book.html_path and Path(book.html_path).exists():
                os.remove(book.html_path)
            
            if book.pdf_path and Path(book.pdf_path).exists():
                os.remove(book.pdf_path)
            
            if book.images_path and Path(book.images_path).exists():
                shutil.rmtree(book.images_path)
                
        except Exception as e:
            print(f"Ошибка удаления файлов книги {book_id}: {e}")
        
        # Удаляем запись из БД
        await db.delete(book)
        await db.commit()
        return True
    
    @staticmethod
    async def create_book_from_run(
        db: AsyncSession,
        run_id: str,
        clerk_user_id: str,
        custom_title: Optional[str] = None
    ) -> Optional[Book]:
        """Создать книгу на основе существующего run_id (автосохранение)"""
        # Проверяем, не создана ли уже книга для этого run_id
        existing_book = await BookService.get_book_by_run_id(db, run_id, clerk_user_id)
        if existing_book:
            return existing_book
        
        # Определяем пути к файлам
        run_dir = Path("data") / run_id
        html_file = run_dir / "book.html"
        pdf_file = run_dir / "book.pdf"
        images_dir = run_dir / "images"
        posts_file = run_dir / "posts.json"
        
        if not html_file.exists() and not pdf_file.exists():
            return None
        
        # Загружаем данные профиля
        profile_data = {}
        if posts_file.exists():
            try:
                posts_data = json.loads(posts_file.read_text(encoding="utf-8"))
                if posts_data:
                    profile = posts_data[0]
                    profile_data = {
                        "username": profile.get("username"),
                        "fullName": profile.get("fullName"),
                        "followersCount": profile.get("followersCount"),
                        "postsCount": len(profile.get("latestPosts", []))
                    }
            except:
                pass
        
        # Определяем название книги
        title = custom_title
        if not title and profile_data.get("fullName"):
            title = f"Для {profile_data['fullName']} с любовью"
        elif not title and profile_data.get("username"):
            title = f"Для @{profile_data['username']} с любовью"
        else:
            title = "Романтическая книга"
        
        # Создаем книгу
        book = await BookService.create_book(
            db=db,
            clerk_user_id=clerk_user_id,
            run_id=run_id,
            title=title,
            profile_data=profile_data,
            html_path=str(html_file) if html_file.exists() else None,
            pdf_path=str(pdf_file) if pdf_file.exists() else None,
            images_path=str(images_dir) if images_dir.exists() else None,
            metadata={"auto_saved": True}
        )
        
        return book
    
    @staticmethod
    def get_book_stats(books: List[Book]) -> Dict[str, int]:
        """Получить статистику по книгам"""
        return {
            "total": len(books),
            "pdf_count": sum(1 for book in books if book.has_pdf),
            "html_count": sum(1 for book in books if book.has_html),
            "completed_count": sum(1 for book in books if book.is_completed)
        } 