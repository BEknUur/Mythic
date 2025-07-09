import importlib
from pathlib import Path

# Импортируем новую функцию генерации
from app.services.book_builder import generate_text_pages

def fallback_pages(image_names: list[str], raw_comments: list[str]) -> list[str]:
    """Генерирует стандартные тексты, если ИИ не справился."""
    return [
        "Момент, застывший во времени.",
        "История, рассказанная одним взглядом.",
        "Красота в каждой детали.",
        "Воспоминание, которое останется навсегда.",
        "Энергия, которую можно почувствовать.",
        "Улыбка, которая меняет мир.",
        "Просто, но с глубоким смыслом."
    ] * (len(image_names) // 7 + 1) # Чтобы текстов точно хватило

async def build_book(style: str, run_id: str, images: list, comments: list, book_format: str, user_id: str):
    """
    Диспетчер, который выбирает и динамически импортирует нужный сборщик книги.
    """
    print(f"▶️ Запуск сборки: стиль='{style}', формат='{book_format}', run_id='{run_id}'")

    # Для flipbook отдельная логика, не зависящая от стиля
    if book_format == 'flipbook':
        try:
            from app.services.flipbook_builder import generate_pages_html, build_flipbook_html
            
            image_names = [Path(p).name for p in images]

            try:
                # Новый асинхронный вызов ИИ
                text_pages = await generate_text_pages(run_id, style, image_names, comments)
            except Exception as e:
                print(f"💔 Ошибка пакетной генерации текстов: {e}. Использую fallback тексты.")
                text_pages = fallback_pages(image_names, comments)

            # Вызываем сборщик HTML с уже готовыми текстами
            pages = generate_pages_html(run_id, images, text_pages)
            build_flipbook_html(run_id, pages)
            print(f"✅ Flipbook для стиля '{style}' успешно сгенерирован.")
        except Exception as e:
            print(f"❌ Ошибка при создании flipbook: {e}")
        return

    # Динамический импорт и вызов сборщика для классических форматов
    try:
        # Имя модуля соответствует стилю (e.g., 'romantic', 'fantasy')
        style_module = importlib.import_module(f".{style}", package="app.styles")
        
        # Имя функции строится по шаблону 'build_STYLE_book'
        build_function_name = f"build_{style}_book"
        
        # Получаем функцию из модуля
        build_function = getattr(style_module, build_function_name)
        
        # Вызываем нужный сборщик
        build_function(run_id, images, comments, book_format, user_id)
        
        print(f"✅ Книга в стиле '{style}' (формат: {book_format}) успешно сгенерирована.")

    except (ImportError, AttributeError):
        print(f"⚠️ Не найден сборщик для стиля '{style}'. Используется 'romantic' по умолчанию.")
        # Фоллбэк на романтический стиль, если нужный модуль или функция не найдены
        from .romantic import build_romantic_book
        build_romantic_book(run_id, images, comments, book_format, user_id)
    except Exception as e:
        print(f"❌ Ошибка при сборке книги в стиле '{style}': {e}")