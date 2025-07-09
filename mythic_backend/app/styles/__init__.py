import importlib
from pathlib import Path
from app.services.text_collector import collect_texts
from app.services.book_builder import generate_text_pages

def fallback_pages(image_names: list[str], raw_comments: list[str]) -> list[str]:
    """Возвращает короткие текстовые заглушки если LLM не сработал"""
    return [f"Описание к фотографии {i+1}: {(raw_comments[i] if i < len(raw_comments) else 'Особенный момент')[:100]}..." 
            for i in range(len(image_names))]

async def build_book(style: str, run_id: str, images: list, comments: list, book_format: str, user_id: str):
    """
    Диспетчер, который выбирает и динамически импортирует нужный сборщик книги.
    """
    print(f"▶️ Запуск сборки: стиль='{style}', формат='{book_format}', run_id='{run_id}'")

    # Для flipbook отдельная логика, не зависящая от стиля
    if book_format == 'flipbook':
        try:
            from app.services.flipbook_builder import generate_pages_html, build_flipbook_html
            
            # Собираем все тексты из постов и сторис - уже есть в comments
            image_names = [Path(p).name for p in images]

            try:
                # Новый асинхронный вызов ИИ с полным контекстом
                text_pages = await generate_text_pages(
                    run_id=run_id, 
                    style=style, 
                    image_names=image_names, 
                    raw_comments=comments
                )
            except Exception as e:
                print(f"💔 LLM-ошибка: {e} — fallback коротких текстов")
                text_pages = fallback_pages(image_names, comments)

            # Вызываем сборщик HTML с уже готовыми текстами
            pages = generate_pages_html(run_id, images, text_pages)
            build_flipbook_html(run_id, pages)
            print(f"✅ Flipbook для стиля '{style}' успешно сгенерирован.")
        except Exception as e:
            print(f"❌ Ошибка при создании flipbook: {e}")
            raise
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
        raise