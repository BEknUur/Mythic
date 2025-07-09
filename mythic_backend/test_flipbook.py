#!/usr/bin/env python3
"""
Тестовый скрипт для проверки генерации флипбука
"""

import asyncio
import json
import tempfile
from pathlib import Path
from app.services.flipbook_builder import generate_pages_html, build_flipbook_html
from app.styles import build_book

async def test_flipbook_generation():
    """Тестирует генерацию флипбука с примерными данными"""
    print("🧪 Начинаем тест генерации флипбука...")
    
    # Создаем временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        test_run_id = "test_run_12345"
        test_dir = Path(temp_dir) / "data" / test_run_id
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем тестовый posts.json
        test_posts = [{
            "username": "test_user",
            "fullName": "Тестовый Пользователь",
            "biography": "Люблю закаты и хорошую музыку",
            "latestPosts": [
                {"caption": "Прекрасный день с друзьями! #счастье #дружба"},
                {"caption": "Закат в горах 🌄 #природа #красота"},
                {"caption": "Новое кафе в центре города #кофе #уют"},
                {"caption": "Вечер с книгой и чаем ☕ #релакс #чтение"}
            ]
        }]
        
        posts_file = test_dir / "posts.json"
        posts_file.write_text(json.dumps(test_posts, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # Создаем директорию с тестовыми изображениями
        images_dir = test_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Создаем фиктивные пути к изображениям
        test_images = [
            str(images_dir / "photo1.jpg"),
            str(images_dir / "photo2.jpg"),
            str(images_dir / "photo3.jpg")
        ]
        
        # Создаем пустые файлы изображений для теста
        for img_path in test_images:
            Path(img_path).touch()
        
        # Тестовые комментарии (очищенные от хэштегов)
        test_comments = [
            "Прекрасный день с друзьями!",
            "Закат в горах",
            "Новое кафе в центре города",
            "Вечер с книгой и чаем"
        ]
        
        print(f"📁 Тестовая директория: {test_dir}")
        print(f"📷 Тестовые изображения: {len(test_images)}")
        print(f"💬 Тестовые комментарии: {len(test_comments)}")
        
        # Меняем рабочую директорию для теста
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Тестируем генерацию страниц
            print("\n🔨 Генерируем страницы...")
            pages = generate_pages_html(test_run_id, test_images, test_comments)
            print(f"✅ Сгенерировано {len(pages)} страниц")
            
            # Тестируем сборку HTML
            print("\n📖 Собираем HTML...")
            build_flipbook_html(test_run_id, pages)
            
            html_file = Path("data") / test_run_id / "book.html"
            if html_file.exists():
                print(f"✅ HTML файл создан: {html_file}")
                print(f"📏 Размер файла: {html_file.stat().st_size} байт")
                
                # Читаем и анализируем содержимое
                content = html_file.read_text(encoding="utf-8")
                page_count = content.count('<div class="page')
                print(f"📄 Найдено страниц в HTML: {page_count}")
                
                if "Романтическая История" in content:
                    print("✅ Заголовок найден")
                if "Тестовый Пользователь" in content:
                    print("✅ Имя пользователя найден")
                if "Пролог" in content:
                    print("✅ Пролог найден")
                if "Эпилог" in content:
                    print("✅ Эпилог найден")
                    
            else:
                print("❌ HTML файл не был создан")
                
            # Тестируем полную сборку через диспетчер
            print("\n🏗️ Тестируем полную сборку через диспетчер...")
            await build_book(
                style="romantic",
                run_id=test_run_id,
                images=test_images,
                comments=test_comments,
                book_format="flipbook",
                user_id="test_user_123"
            )
            print("✅ Полная сборка завершена")
            
        finally:
            os.chdir(original_cwd)
    
    print("\n🎉 Тест завершен!")

if __name__ == "__main__":
    asyncio.run(test_flipbook_generation()) 