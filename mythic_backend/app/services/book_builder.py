import json
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from app.services.llm_client import strip_cliches, analyze_photo_for_memoir, generate_memoir_chapter
from typing import List, Tuple, Optional
import random
import time
import re
import asyncio
from fpdf import FPDF
from pydantic import BaseModel
import concurrent.futures

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy не установлен, некоторые эффекты будут недоступны")

# Pydantic модели для фэнтези-книги
class FantasyChapter(BaseModel):
    key: str
    title: str
    text: str

class FantasyBook(BaseModel):
    title: str
    chapters: List[FantasyChapter]
    final_message: str

# Асинхронная функция-агент для быстрой генерации фэнтези-книги
async def generate_fantasy_book_agent(chapter_configs: List[dict], context_data: dict, quick_fallbacks: dict) -> FantasyBook:
    """Асинхронно генерирует все главы фэнтези-книги параллельно"""
    
    async def generate_chapter_async(config: dict, fallback: str) -> FantasyChapter:
        """Генерирует одну главу асинхронно с таймаутом"""
        try:
            # Таймаут 20 секунд на главу
            chapter_text = await asyncio.wait_for(
                async_generate_memoir_chapter("fantasy_chapter", {
                    'prompt': config['prompt'],
                    'context': context_data,
                    'style': 'epic_fantasy'
                }),
                timeout=20.0
            )
            
            # Проверяем качество результата
            if not chapter_text or len(chapter_text.strip()) < 100:
                print(f"⚡ Короткий ответ для '{config['title']}', использую fallback")
                chapter_text = fallback
            else:
                chapter_text = strip_cliches(chapter_text)
                chapter_text = format_chapter_text(chapter_text)
            
            return FantasyChapter(
                key=config['key'],
                title=config['title'],
                text=chapter_text
            )
            
        except asyncio.TimeoutError:
            print(f"⏰ Таймаут для главы '{config['title']}', использую fallback")
            return FantasyChapter(
                key=config['key'],
                title=config['title'],
                text=fallback
            )
        except Exception as e:
            print(f"💔 Ошибка генерации главы '{config['title']}': {e}")
            return FantasyChapter(
                key=config['key'],
                title=config['title'],
                text=fallback
            )
    
    # Генерируем все главы параллельно
    print("🚀 Запускаю параллельную генерацию всех глав...")
    start_time = time.time()
    
    tasks = [
        generate_chapter_async(config, quick_fallbacks.get(config['key'], f"Глава о {config['title'].lower()} полна магии и древних тайн."))
        for config in chapter_configs
    ]
    
    chapters = await asyncio.gather(*tasks)
    
    # Генерируем финальное послание
    final_message = "Пусть твоя сага будет вечной, а имя — вписано в Книгу Героев!"
    try:
        final_prompt = f"Напиши короткое финальное послание для фэнтези-книги о {context_data.get('full_name', 'герое')}."
        
        final_message = await asyncio.wait_for(
            async_generate_memoir_chapter("final_message", {
                'prompt': final_prompt,
                'context': context_data,
                'style': 'epic_fantasy'
            }),
            timeout=10.0
        )
        
        if not final_message or len(final_message.strip()) < 10:
            final_message = "Пусть твоя сага будет вечной, а имя — вписано в Книгу Героев!"
            
    except Exception as e:
        print(f"💔 Ошибка генерации финального послания: {e}")
        final_message = "Пусть твоя сага будет вечной, а имя — вписано в Книгу Героев!"
    
    # Генерируем название книги
    full_name = context_data.get('full_name', 'героя')
    book_titles = [
        f"Хроники {full_name}",
        f"Летопись великого героя {full_name}",
        f"Сага о {full_name}",
        f"Песнь магии и судьбы {full_name}",
        f"Завет древних для {full_name}"
    ]
    book_title = random.choice(book_titles)
    
    total_time = time.time() - start_time
    print(f"⏱️ Все главы сгенерированы за {total_time:.1f} секунд")
    
    return FantasyBook(
        title=book_title,
        chapters=chapters,
        final_message=final_message
    )

# Синхронная обертка для запуска асинхронного агента
def run_fantasy_book_agent_sync(chapter_configs: List[dict], context_data: dict, quick_fallbacks: dict) -> FantasyBook:
    """Синхронная обертка для запуска асинхронного агента"""
    try:
        # Проверяем, есть ли уже запущенный event loop
        try:
            loop = asyncio.get_running_loop()
            # Если loop уже запущен, создаем новую задачу
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, generate_fantasy_book_agent(chapter_configs, context_data, quick_fallbacks))
                return future.result()
        except RuntimeError:
            # Если нет запущенного loop, используем asyncio.run
            return asyncio.run(generate_fantasy_book_agent(chapter_configs, context_data, quick_fallbacks))
    except Exception as e:
        print(f"❌ Ошибка запуска агента: {e}")
        # Возвращаем fallback книгу
        chapters = [
            FantasyChapter(
                key=config['key'],
                title=config['title'],
                text=quick_fallbacks.get(config['key'], f"Глава о {config['title'].lower()} полна магии и древних тайн.")
            )
            for config in chapter_configs
        ]
        return FantasyBook(
            title=f"Хроники {context_data.get('full_name', 'героя')}",
            chapters=chapters,
            final_message="Пусть твоя сага будет вечной, а имя — вписано в Книгу Героев!"
        )

# Асинхронная версия generate_memoir_chapter
async def async_generate_memoir_chapter(chapter_type: str, params: dict) -> str:
    """Асинхронная версия generate_memoir_chapter"""
    try:
        from app.services.llm_client import async_client, settings
        
        prompt = params.get('prompt', '')
        context = params.get('context', {})
        style = params.get('style', 'epic_fantasy')
        
        # Формируем сообщение для LLM (сокращенное)
        system_message = f"Ты — мастер эпического фэнтези. Создавай тексты в стиле {style}."
        user_message = f"{prompt}"
        
        response = await async_client.chat.completions.create(
            model=settings.AZURE_OPENAI_GPT4_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=800  # Минимальный лимит токенов
        )
        
        result = response.choices[0].message.content.strip()
        return result if result else ""
        
    except Exception as e:
        print(f"❌ Ошибка async_generate_memoir_chapter: {e}")
        return ""

def analyze_profile_data(posts_data: list) -> dict:
    if not posts_data:
        return {}
    
    profile = posts_data[0]
    posts = profile.get("latestPosts", [])
    
    analysis = {
        "username": profile.get("username", "Unknown"),
        "full_name": profile.get("fullName", ""),
        "bio": profile.get("biography", ""),
        "followers": profile.get("followersCount", 0),
        "following": profile.get("followsCount", 0),
        "posts_count": len(posts),
        "verified": profile.get("verified", False),
        "profile_pic": profile.get("profilePicUrl", ""),
        "locations": [],
        "captions": [],
        "hashtags": set(),
        "mentions": set(),
        "post_details": [],
        "total_likes": 0,
        "total_comments": 0,
        "post_dates": [],
        "most_liked_post": None,
        "most_commented_post": None,
        "common_hashtags": [],
        "mentioned_users": []
    }
    
    # Собираем детальную информацию о постах
    for post in posts:
        post_info = {
            "caption": post.get("caption", ""),
            "location": post.get("locationName", ""),
            "likes": post.get("likesCount", 0),
            "comments": post.get("commentsCount", 0),
            "type": post.get("type", ""),
            "alt": post.get("alt", ""),
            "timestamp": post.get("timestamp", ""),
            "hashtags": post.get("hashtags", []),
            "mentions": post.get("mentions", []),
            "url": post.get("url", "")
        }
        analysis["post_details"].append(post_info)
        
        # Накапливаем статистику
        if post.get("likesCount"):
            analysis["total_likes"] += post["likesCount"]
            if not analysis["most_liked_post"] or post["likesCount"] > analysis["most_liked_post"]["likes"]:
                analysis["most_liked_post"] = post_info
                
        if post.get("commentsCount"):
            analysis["total_comments"] += post["commentsCount"]
            if not analysis["most_commented_post"] or post["commentsCount"] > analysis["most_commented_post"]["comments"]:
                analysis["most_commented_post"] = post_info
        
        if post.get("locationName"):
            analysis["locations"].append(post["locationName"])
        
        if post.get("caption"):
            analysis["captions"].append(post["caption"])
        
        if post.get("timestamp"):
            analysis["post_dates"].append(post["timestamp"])
            
        analysis["hashtags"].update(post.get("hashtags", []))
        analysis["mentions"].update(post.get("mentions", []))
    
    # Анализируем популярные хэштеги
    hashtag_count = {}
    for post in posts:
        for hashtag in post.get("hashtags", []):
            hashtag_count[hashtag] = hashtag_count.get(hashtag, 0) + 1
    
    analysis["common_hashtags"] = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)[:5]
    analysis["mentioned_users"] = list(analysis["mentions"])[:10]
    
    return analysis

def build_romantic_book(run_id: str, images: list[Path], texts: str, book_format: str = "classic", user_id: str = None):
    """Создание HTML книги"""
    try:
        
        run_dir = Path("data") / run_id
        posts_json = run_dir / "posts.json"
        images_dir = run_dir / "images"
        
        if posts_json.exists():
            posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
        else:
            posts_data = []
        
        
        analysis = analyze_profile_data(posts_data)
        username = analysis.get("username", "...")
        
        
        actual_images = []
        if images_dir.exists():
            # Собираем все изображения из папки
            for img_file in sorted(images_dir.glob("*")):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    actual_images.append(img_file)
        
        # Романтические сообщения о процессе анализа
        romantic_analysis_messages = [
            f"Погружаюсь в глубину взгляда @{username}... Каждый пиксель рассказывает историю",
            f"Анализирую магию ваших глаз... В них читается целая жизнь и характер",
            f"Изучаю изгибы вашей улыбки — она способна растопить самые холодные сердца",
            f"Рассматриваю игру света на ваших чертах лица... Природа создала совершенство",
            f"Анализирую выражения ваших глаз — каждое фото рассказывает новую главу истории"
        ]
        
        romantic_photo_messages = [
            f"Бережно сохраняю {len(actual_images)} ваших драгоценных моментов жизни...",
            f"Каждое из {len(actual_images)} фото — произведение искусства в моей личной коллекции",
            f"Собрал {len(actual_images)} кадров вашей красоты — теперь они навсегда останутся со мной",
            f"{len(actual_images)} фотографий вашей души надёжно сохранены в памяти сердца",
            f"Архивирую {len(actual_images)} мгновений вашей жизни с особой нежностью и вниманием"
        ]
        
        print(random.choice(romantic_analysis_messages))
        print(random.choice(romantic_photo_messages))
        
        # Генерируем контент в зависимости от формата
        content = {"format": "literary"}  
        html = create_literary_instagram_book_html(content, analysis, actual_images)
        
        out = Path("data") / run_id
        out.mkdir(parents=True, exist_ok=True)
        
        html_file = out / "book.html"
        html_file.write_text(html, encoding="utf-8")
        
        # Генерируем PDF версию
        try:
            pdf_file = out / "book.pdf"
            # Создаем красивый PDF из HTML контента с помощью WeasyPrint
            create_pdf_with_weasyprint(pdf_file, html)
            print(f"📄 Красивая PDF версия создана: {pdf_file}")
        except Exception as pdf_error:
            print(f"❌ Ошибка создания PDF: {pdf_error}")
        
        # Автоматическое сохранение в библиотеку пользователя
        if user_id:
            try:
                import uuid
                import datetime
                import shutil
                
                # Получаем данные профиля для названия книги
                profile_username = analysis.get("username")
                profile_full_name = analysis.get("full_name")
                
                # Генерируем уникальный ID для книги
                book_id = str(uuid.uuid4())
                
                # Определяем название книги
                title = f"Для {profile_full_name or profile_username or 'Неизвестный'} с любовью"
                
                # Функции для работы с библиотекой пользователя (локальные копии)
                def get_user_books_db_path_local(user_id: str) -> Path:
                    user_books_dir = Path("data") / "user_books"
                    user_books_dir.mkdir(parents=True, exist_ok=True)
                    return user_books_dir / f"{user_id}.json"

                def load_user_books_local(user_id: str) -> list[dict]:
                    books_file = get_user_books_db_path_local(user_id)
                    if not books_file.exists():
                        return []
                    try:
                        return json.loads(books_file.read_text(encoding="utf-8"))
                    except:
                        return []

                def save_user_books_local(user_id: str, books: list[dict]):
                    books_file = get_user_books_db_path_local(user_id)
                    books_file.write_text(json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8")

                def copy_book_to_user_library_local(run_id: str, user_id: str, book_id: str) -> bool:
                    try:
                        source_dir = Path("data") / run_id
                        user_library_dir = Path("data") / "user_books" / user_id / book_id
                        user_library_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Копируем файлы книги
                        for file in ["book.html", "book.pdf", "posts.json"]:
                            source_file = source_dir / file
                            if source_file.exists():
                                shutil.copy2(source_file, user_library_dir / file)
                        
                        # Копируем папку с изображениями
                        source_images = source_dir / "images"
                        if source_images.exists():
                            target_images = user_library_dir / "images"
                            if target_images.exists():
                                shutil.rmtree(target_images)
                            shutil.copytree(source_images, target_images)
                        
                        return True
                    except Exception as e:
                        print(f"Ошибка копирования книги {run_id} для пользователя {user_id}: {e}")
                        return False
                
                # Загружаем существующие книги пользователя
                books = load_user_books_local(user_id)
                
                # Проверяем, не сохранена ли уже эта книга
                already_saved = False
                for book in books:
                    if book["run_id"] == run_id:
                        already_saved = True
                        break
                
                if not already_saved:
                    # Копируем файлы книги в библиотеку пользователя
                    if copy_book_to_user_library_local(run_id, user_id, book_id):
                        # Добавляем книгу в список
                        new_book = {
                            "id": book_id,
                            "run_id": run_id,
                            "title": title,
                            "created_at": datetime.datetime.now().isoformat(),
                            "profile_username": profile_username,
                            "profile_full_name": profile_full_name,
                            "has_pdf": pdf_file.exists(),
                            "has_html": html_file.exists()
                        }
                        
                        books.append(new_book)
                        save_user_books_local(user_id, books)
                        
                        print(f"📚 Книга автоматически сохранена в библиотеку пользователя {user_id}")
                    else:
                        print("❌ Ошибка автоматического сохранения книги в библиотеку")
                else:
                    print("📚 Книга уже была сохранена в библиотеке пользователя")
                    
            except Exception as save_error:
                print(f"❌ Ошибка автоматического сохранения: {save_error}")
        
        final_messages = [
            f"Магия свершилась! Романтическая книга о @{username} готова к прочтению: {html_file}",
            f"Ваша персональная книга любви создана! @{username}, вы теперь — литературный герой: {html_file}",
            f"Летопись красоты @{username} завершена! Каждая страница пропитана искренним восхищением: {html_file}",
            f"Книга-посвящение @{username} готова! В ней живёт частичка души автора: {html_file}"
        ]
        print(random.choice(final_messages))
        
    except Exception as e:
        print(f"Ошибка при создании книги о @{username}: {e}")
        # Создаем базовую версию при ошибке
        try:
            basic_html = f"""
            <html>
            <head>
                <title>Книга</title>
                <style>
                    body {{ background: white; font-family: serif; padding: 20px; }}
                    .error {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Книга</h1>
                    <p>Извините, произошла ошибка при создании книги: {e}</p>
                    <p>Попробуйте еще раз позже</p>
                </div>
            </body>
            </html>
            """
            html_file = Path("data") / run_id / "book.html"
            html_file.write_text(basic_html, encoding="utf-8")
            
        except Exception as final_error:
            print(f"Критическая ошибка: {final_error}")

def apply_dream_pastel_effect(img: Image.Image) -> Image.Image:
    """Применяет эффект Dream-Pastel к изображению"""
    try:
        # Проверяем, что изображение валидное
        if img is None or img.size[0] == 0 or img.size[1] == 0:
            print("❌ Недопустимое изображение для обработки")
            return img
            
        # Конвертируем в RGB если нужно
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
      
        img = img.filter(ImageFilter.GaussianBlur(1.2))
        
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
        
       
        overlay = Image.new('RGBA', img.size, (255, 220, 210, 25)) 
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        
        if NUMPY_AVAILABLE:
            try:
                noise = np.random.randint(0, 15, (img.size[1], img.size[0], 3), dtype=np.uint8)
                noise_img = Image.fromarray(noise, 'RGB').convert('RGBA')
                noise_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                noise_overlay.paste(noise_img, (0, 0))
                img = Image.alpha_composite(img, noise_overlay)
            except Exception as noise_error:
                print(f"❌ Ошибка при добавлении шума: {noise_error}")
        else:
            print("⚠️ Пропускаем добавление шума (numpy недоступен)")
        return img.convert('RGB')
        # Легкое увеличение яркости
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        
        return img.convert('RGB')
    except Exception as e:
        print(f"❌ Ошибка при применении Dream-Pastel эффекта: {e}")
        # Возвращаем оригинальное изображение при ошибке
        return img.convert('RGB') if img.mode != 'RGB' else img

def create_collage_spread(img1: Image.Image, img2: Image.Image, caption: str) -> str:
    """Создает HTML-блок для разворота с коллажом из двух фото и подписью."""
    
    # Конвертируем изображения в base64
    img1_base64 = base64.b64encode(img1.tobytes()).decode()
    img2_base64 = base64.b64encode(img2.tobytes()).decode()
    
    collage_html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Коллаж</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .collage-container {{
            display: flex;
            justify-content: space-between;
            padding: 20px;
        }}
        .photo-container {{
            width: 48%;
            position: relative;
        }}
        .photo-container img {{
            width: 100%;
            height: 300px;
            object-fit: cover;
        }}
        .caption {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.5);
            color: #fff;
            padding: 5px;
        }}
    </style>
</head>
<body>
    <div class="collage-container">
        <div class="photo-container">
            <img src="data:image/jpeg;base64,{img1_base64}" alt="Фото 1">
            <div class="caption">{caption}</div>
        </div>
        <div class="photo-container">
            <img src="data:image/jpeg;base64,{img2_base64}" alt="Фото 2">
            <div class="caption">{caption}</div>
        </div>
    </div>
</body>
</html>
    """
    
    return collage_html


def analyze_photo_for_gender(img_path: Path) -> str:
    """Анализирует фото для определения пола через ИИ"""
    try:
        from app.services.llm_client import generate_text
        
        with Image.open(img_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Уменьшаем размер для анализа
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=80)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            img_data = f"data:image/jpeg;base64,{img_str}"
            
            prompt = """Проанализируй это фото и определи пол человека. 
            
            Ответь ТОЛЬКО одним словом:
            - "female" если это девушка/женщина
            - "male" если это парень/мужчина
            
            Смотри на черты лица, прическу, одежду, общий вид."""
            
            # Используем vision model для анализа
            result = generate_text(prompt, max_tokens=10, temperature=0.1, image_data=img_data)
            
            if "female" in result.lower():
                return "female"
            elif "male" in result.lower():
                return "male"
            else:
                return "unknown"
                
    except Exception as e:
        print(f"❌ Ошибка анализа пола по фото: {e}")
        return "unknown"

def analyze_gender_with_ai(full_name: str, detected_gender: str) -> dict:
    """Анализирует пол через ИИ и возвращает правильные местоимения"""
    try:
        from app.services.llm_client import generate_text
        
        prompt = f"""Проанализируй информацию о человеке и определи пол, затем выбери правильные местоимения для русского языка.

ИНФОРМАЦИЯ:
- Имя: {full_name}
- Анализ фото: {detected_gender}

ВАЖНО: Внимательно анализируй имя! Вот примеры:

ЖЕНСКИЕ ИМЕНА (используй "female"):
- Русские: Анна, Мария, Елена, Арина, Дарья, Алина, Юлия, Екатерина, Ольга, Татьяна, Наталья, Светлана, Ирина, Валерия, Виктория, Диана, Карина, Кристина, Маргарита, Милана, Полина, Лиана, Лилия, Лидия, Людмила, Вера, Надежда, Любовь
- Казахские: Аружан, Аида, Амина, Асель, Акбота, Гульнара, Динара, Камила, Лейла, Мадина, Назгуль, Сауле
- Европейские: Emma, Kate, Anna, Elena, Sofia, Daria, Julia, Kristina, Victoria, Diana, Alice, Maria, Natasha, Alexandra, Elizabeth, Sarah, Jessica, Nicole, Amanda, Melissa
- Уменьшительные: Аня, Катя, Лена, Маша, Оля, Таня, Наташа, Света, Ира, Юля, Настя, Лера, Вика, Кристи, Рита, Поля, Лиля

МУЖСКИЕ ИМЕНА (используй "male"):
- Русские: Александр, Алексей, Андрей, Антон, Артем, Дмитрий, Максим, Михаил, Никита, Иван, Игорь, Олег, Павел, Сергей, Владимир, Денис, Евгений, Кирилл
- Казахские: Азамат, Арман, Данияр, Ерлан, Кайрат, Марат, Нурлан, Рустам
- Европейские: John, Michael, David, William, Richard, Daniel, Paul, Mark, Andrew, Kevin, Brian
- Уменьшительные: Саша, Женя, Леша, Дима, Вова, Слава, Макс, Миша, Коля, Паша

ПРАВИЛА ОПРЕДЕЛЕНИЯ:
1. Если имя в списке женских - обязательно "female"
2. Если имя заканчивается на -а, -я, -ия, -на - скорее всего "female" 
3. Лиана, Диана, Анна, Мария, София, Арина - это ЖЕНСКИЕ имена
4. Если анализ фото показал "female" - это дополнительное подтверждение
5. В случае сомнений - лучше ошибиться в сторону более вежливого обращения

Ответь СТРОГО в формате JSON:
{{
    "gender": "female" или "male",
    "gender_word": "красивая" или "красивый", 
    "she_he": "она" или "он",
    "her_his": "её" или "его",
    "love_word": "влюблен в неё" или "влюблен в него"
}}

Для имени "{full_name}" правильный ответ:"""

        result = generate_text(prompt, max_tokens=200, temperature=0.0)  # Снижаем температуру для точности
        
        # Пытаемся распарсить JSON
        import json
        try:
            # Извлекаем JSON из ответа
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = result[start:end]
                gender_data = json.loads(json_str)
                
                # Проверяем что все поля на месте
                required_fields = ['gender', 'gender_word', 'she_he', 'her_his', 'love_word']
                if all(field in gender_data for field in required_fields):
                    print(f"✅ ИИ определил пол: {gender_data['gender']} для имени '{full_name}' -> {gender_data['she_he']}")
                    return gender_data
                    
        except Exception as parse_error:
            print(f"❌ Ошибка парсинга JSON от ИИ: {parse_error}")
        
        # Более умный fallback с анализом имени
        print("⚡ ИИ не смог определить, использую умный fallback")
        
        # Определяем пол по имени для fallback
        name_lower = full_name.lower().strip()
        
        # Женские признаки в имени
        female_indicators = [
            'лиана', 'диана', 'анна', 'мария', 'арина', 'елена', 'софия', 'дарья', 'алина', 
            'юлия', 'екатерина', 'ольга', 'татьяна', 'наталья', 'светлана', 'ирина',
            'валерия', 'виктория', 'карина', 'кристина', 'милана', 'полина', 'лилия',
            'аружан', 'аида', 'амина', 'асель', 'emma', 'kate', 'sofia', 'alice'
        ]
        
        # Проверяем на женские имена
        is_female = any(indicator in name_lower for indicator in female_indicators)
        
        # Проверяем окончания
        if not is_female:
            female_endings = ['ана', 'ина', 'ена', 'она', 'ьяна', 'ия', 'я', 'а']
            is_female = any(name_lower.endswith(ending) for ending in female_endings)
        
        # Учитываем анализ фото
        if detected_gender == "female":
            is_female = True
        
        if is_female or "female" in result.lower():
            return {
                "gender": "female",
                "gender_word": "красивая",
                "she_he": "она", 
                "her_his": "её",
                "love_word": "влюблен в неё"
            }
        else:
            return {
                "gender": "male",
                "gender_word": "красивый",
                "she_he": "он",
                "her_his": "его", 
                "love_word": "влюблен в него"
            }
            
    except Exception as e:
        print(f"❌ Ошибка анализа пола через ИИ: {e}")
        
        # Безопасный fallback - анализируем имя локально
        name_lower = full_name.lower().strip()
        
        # Явно женские имена
        female_names = [
            'лиана', 'диана', 'анна', 'мария', 'арина', 'елена', 'софия', 'дарья', 
            'алина', 'юлия', 'екатерина', 'ольга', 'татьяна', 'наталья', 'светлана',
            'ирина', 'валерия', 'виктория', 'карина', 'кристина', 'милана', 'полина',
            'аружан', 'аида', 'амина', 'асель', 'emma', 'kate', 'sofia', 'alice', 'maria'
        ]
        
        # Проверяем точные совпадения или вхождения
        is_female = any(fem_name in name_lower for fem_name in female_names)
        
        # Проверяем окончания
        if not is_female:
            female_endings = ['ана', 'ина', 'ена', 'я', 'а']
            is_female = any(name_lower.endswith(ending) and len(name_lower) > 2 for ending in female_endings)
        
        # Учитываем фото
        if detected_gender == "female":
            is_female = True
        
        if is_female:
            print(f"🚺 Fallback определил женский пол для '{full_name}'")
            return {
                "gender": "female",
                "gender_word": "красивая",
                "she_he": "она",
                "her_his": "её", 
                "love_word": "влюблен в неё"
            }
        else:
            print(f"🚹 Fallback определил мужской пол для '{full_name}'")
            return {
                "gender": "male",
                "gender_word": "красивый",
                "she_he": "он",
                "her_his": "его",
                "love_word": "влюблен в него"
            }

def analyze_name_for_gender(name: str) -> str:
    """Анализирует имя для определения пола"""
    if not name:
        return "unknown"
    
    name_lower = name.lower().strip()
    
    # Расширенный список женских имен (русские, казахские, европейские)
    female_names = [
        # Русские женские имена
        'арина', 'анна', 'елена', 'мария', 'ольга', 'татьяна', 'наталья', 'светлана', 
        'ирина', 'екатерина', 'юлия', 'алина', 'дарья', 'алиса', 'анастасия', 
        'валерия', 'виктория', 'диана', 'карина', 'кристина', 'маргарита', 
        'милана', 'полина', 'ульяна', 'людмила', 'галина', 'нина', 'вера', 
        'любовь', 'надежда', 'лариса', 'жанна', 'инна', 'тамара', 'раиса',
        'оксана', 'антонина', 'зинаида', 'клавдия', 'лидия', 'регина',
        
        # Казахские женские имена
        'айгуль', 'айнур', 'аружан', 'аида', 'амина', 'асель', 'акбота',
        'гульнара', 'гульмира', 'динара', 'жанара', 'жамила', 'камила',
        'лейла', 'мадина', 'назгуль', 'сауле', 'толганай', 'шахзода',
        'aruzhan', 'aida', 'amina', 'asel', 'akbota', 'gulnara', 'dinara',
        
        # Европейские женские имена  
        'emma', 'kate', 'anna', 'elena', 'sofia', 'daria', 'julia',
        'kristina', 'milana', 'polina', 'valeria', 'victoria', 'diana',
        'alice', 'maria', 'natasha', 'alexandra', 'elizabeth', 'sarah',
        'jessica', 'nicole', 'amanda', 'melissa', 'stephanie', 'nicole',
        'lisa', 'michelle', 'kimberly', 'donna', 'carol', 'ruth', 'sharon',
        
        # Короткие формы и уменьшительные
        'аня', 'катя', 'лена', 'маша', 'оля', 'таня', 'наташа', 'света',
        'ира', 'катя', 'юля', 'настя', 'лера', 'вика', 'кристи', 'рита',
        'поля', 'ксюша', 'соня', 'даша', 'саша', 'лиза', 'женя'
    ]
    
    # Расширенный список мужских имен
    male_names = [
        # Русские мужские имена
        'александр', 'алексей', 'андрей', 'антон', 'артем', 'борис', 'вадим',
        'валентин', 'василий', 'виктор', 'владимир', 'владислав', 'вячеслав',
        'геннадий', 'георгий', 'григорий', 'денис', 'дмитрий', 'евгений',
        'егор', 'иван', 'игорь', 'илья', 'кирилл', 'константин', 'леонид',
        'максим', 'михаил', 'никита', 'николай', 'олег', 'павел', 'петр',
        'роман', 'сергей', 'станислав', 'тимур', 'федор', 'юрий', 'ярослав',
        
        # Казахские мужские имена
        'абай', 'адильхан', 'азамат', 'айдос', 'айтуган', 'алмас', 'арман',
        'асхат', 'бауыржан', 'берик', 'данияр', 'ерлан', 'жанат', 'кайрат',
        'марат', 'нурлан', 'рустам', 'саят', 'темирлан', 'тимур', 'ұлан',
        'nurlan', 'arman', 'azamat', 'daniyar', 'erlan', 'kairat', 'marat',
        
        # Европейские мужские имена
        'john', 'michael', 'david', 'william', 'richard', 'charles', 'joseph',
        'thomas', 'christopher', 'daniel', 'paul', 'mark', 'donald', 'steven',
        'kenneth', 'andrew', 'joshua', 'kevin', 'brian', 'george', 'edward',
        'ronald', 'timothy', 'jason', 'jeffrey', 'ryan', 'jacob', 'gary',
        
        # Короткие формы и уменьшительные
        'саша', 'женя', 'леша', 'антоша', 'дима', 'вова', 'слава', 'гена',
        'гоша', 'денис', 'коля', 'макс', 'миша', 'никита', 'олег', 'паша',
        'петя', 'рома', 'сережа', 'стас', 'федя', 'юра', 'ярик'
    ]
    
    # Проверяем точные совпадения (полное имя)
    if name_lower in female_names:
        return "female"
    if name_lower in male_names:
        return "male"
    
    # Проверяем вхождения (часть имени)
    for fem_name in female_names:
        if fem_name in name_lower:
            return "female"
    
    for male_name in male_names:
        if male_name in name_lower:
            return "male"
    
    # Проверяем окончания имен
    # Женские окончания
    female_endings = ['а', 'я', 'ия', 'на', 'ра', 'ла', 'га', 'ка', 'та', 'да', 'ча', 'ша']
    for ending in female_endings:
        if name_lower.endswith(ending) and len(name_lower) > 2:
            return "female"
    
    # Мужские окончания  
    male_endings = ['ов', 'ев', 'ин', 'ын', 'ич', 'ей', 'ай', 'ий', 'он', 'ан', 'ен', 'р', 'л', 'н', 'м', 'с']
    for ending in male_endings:
        if name_lower.endswith(ending) and len(name_lower) > 2:
            return "male"
    
    return "unknown"

def create_literary_instagram_book_html(content: dict, analysis: dict, images: list[Path]) -> str:
    """Создает HTML романтическую книгу-подарок от человека к человеку"""
    
    # Используем fullName как основное имя
    full_name = analysis.get('full_name', analysis.get('username', 'дорогой человек'))
    username = analysis.get('username', 'friend')
    followers = analysis.get('followers', 0)
    posts_count = analysis.get('posts_count', 0)
    bio = analysis.get('bio', '')
    
    # Анализируем видео и рилсы из постов
    video_content = []
    real_captions = []
    locations = []
    
    # Собираем данные о видео и постах
    post_details = analysis.get('post_details', [])
    for post in post_details[:10]:  # Берем первые 10 постов
        if post.get('caption'):
            real_captions.append(post['caption'])
        if post.get('location'):
            locations.append(post['location'])
        if post.get('type') in ['video', 'reel']:
            video_content.append({
                'type': post.get('type'),
                'caption': post.get('caption', ''),
                'alt': post.get('alt', '')
            })
    
    # AI-анализ для первых 3 рилсов
    from app.services.media_analyzer import MediaAnalysisRequest, analyze_media_item
    analyzed_reels = []
    for reel in video_content[:3]:
        try:
            req = MediaAnalysisRequest(
                image_path=None,
                caption=reel.get('caption',''),
                alt_text=reel.get('alt',''),
                media_type='reel'
            )
            res = analyze_media_item(req)
            reel['analysis'] = res.description
            reel['mood'] = res.mood
            analyzed_reels.append(reel)
        except Exception as e:
            print(f"media_analyzer reel error: {e}")
            reel['analysis'] = 'Динамичный момент, наполненный энергией'
            analyzed_reels.append(reel)
    
    # Обрабатываем изображения (РАНДОМНЫЙ выбор - не подряд!)
    processed_images = []
    detected_gender = "unknown"
    selected_photo_data = []  # Данные о выбранных фото для анализа
    
    if images:
        # НОВАЯ ЛОГИКА: РАНДОМНЫЙ выбор 7 фото из всего массива
        import random
        
        total_images = len(images)
        print(f"📸 Всего фото в профиле: {total_images}")
        
        if total_images >= 7:
            # Если фото много - берем 7 случайных без повторов
            selected_indices = random.sample(range(total_images), 7)
            selected_indices.sort()  # Сортируем для красивого вывода
        elif total_images >= 4:
            # Если фото мало - берем все + добавляем случайные дубли до 7
            selected_indices = list(range(total_images))
            while len(selected_indices) < 7:
                random_idx = random.randint(0, total_images - 1)
                selected_indices.append(random_idx)
        else:
            # Если фото очень мало - дублируем случайным образом до 7
            selected_indices = []
            for _ in range(7):
                random_idx = random.randint(0, total_images - 1)
                selected_indices.append(random_idx)
        
        print(f"📸 Рандомный выбор: из {total_images} выбрал позиции {selected_indices}")
        
        # Анализируем первое ВЫБРАННОЕ фото для определения пола
        if images and selected_indices and images[selected_indices[0]].exists():
            print("🔍 Анализирую первое выбранное фото для определения пола...")
            detected_gender = analyze_photo_for_gender(images[selected_indices[0]])
            print(f"✅ Определен пол: {detected_gender}")
        
        # Обрабатываем выбранные фотографии (7 штук рандомно)
        for i, idx in enumerate(selected_indices):
            img_path = images[idx]
            if img_path.exists():
                try:
                    with Image.open(img_path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Оптимальный размер для чтения
                        max_size = (700, 500)
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        
                        # Мягкая обработка для романтического стиля
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(1.05)
                        enhancer = ImageEnhance.Color(img)
                        img = enhancer.enhance(1.1)
                        
                        buffer = BytesIO()
                        img.save(buffer, format='JPEG', quality=90)
                        img_str = base64.b64encode(buffer.getvalue()).decode()
                        processed_images.append(f"data:image/jpeg;base64,{img_str}")
                        
                        # ИИ анализ фото для генерации описания (исправленный)
                        photo_analysis = ""
                        try:
                            print(f"🧠 ИИ анализирует фото #{idx+1} для создания описания...")
                            
                            # Попробуем разные способы импорта
                            try:
                                from app.services.media_analyzer import MediaAnalysisRequest, analyze_media_item
                                req = MediaAnalysisRequest(image_path=img_path)
                                ai_result = analyze_media_item(req)
                                photo_analysis = ai_result.description
                                print(f"✅ ИИ анализ через media_analyzer: {photo_analysis[:50]}...")
                            except Exception as import_error:
                                print(f"⚠️ media_analyzer недоступен: {import_error}")
                                
                                # Fallback: используем прямой анализ через LLM
                                try:
                                    photo_analysis = analyze_photo_for_memoir(img_path, f"Instagram профиль @{username}", "first_impression")
                                    print(f"✅ ИИ анализ через memoir: {photo_analysis[:50]}...")
                                except:
                                    photo_analysis = ""
                            
                            # Обрезаем описание если оно слишком длинное
                            if photo_analysis and len(photo_analysis) > 120:
                                photo_analysis = photo_analysis[:117] + "..."
                                
                        except Exception as e:
                            print(f"❌ Ошибка ИИ анализа фото #{idx+1}: {e}")
                            photo_analysis = ""
                        
                        # Если ИИ анализ не сработал - используем качественные fallback'ы
                        if not photo_analysis or len(photo_analysis.strip()) < 10:
                            print(f"⚡ Использую fallback описание для фото #{idx+1}")
                            fallback_descriptions = [
                                "Естественная красота в каждой детали",
                                "Взгляд, полный глубины и искренности", 
                                "Особая атмосфера и харизма",
                                "Эмоции, которые говорят без слов",
                                "Магнетическая энергетика личности",
                                "Грация и стиль в каждом движении",
                                "Момент совершенства, застывший в кадре"
                            ]
                            photo_analysis = fallback_descriptions[i % len(fallback_descriptions)]
                        
                        selected_photo_data.append({
                            'index': idx + 1,  # Номер фото в профиле
                            'analysis': photo_analysis,
                            'image': f"data:image/jpeg;base64,{img_str}"
                        })
                        
                        print(f"✅ Обработано фото #{idx+1} из профиля: '{photo_analysis[:30]}...'")
                except Exception as e:
                    print(f"❌ Ошибка обработки изображения {img_path}: {e}")
    
    # Helper function for safely getting photo analysis from the list
    def get_safe_photo_analysis(index: int, fallback_text: str) -> str:
        """Safely gets photo analysis, cycling through available photos."""
        if not selected_photo_data:
            return fallback_text
        # Cycle through the available photos using modulo
        safe_index = index % len(selected_photo_data)
        return selected_photo_data[safe_index]['analysis']
    
    # Подготавливаем контекст для ИИ с анализом фото
    context_data = {
        'username': username,
        'full_name': full_name,
        'followers': followers,
        'posts_count': posts_count,
        'bio': bio,
        'captions': real_captions[:5],  # Первые 5 подписей
        'locations': locations[:3],     # Первые 3 локации
        'video_content': analyzed_reels[:3],  # проанализированные рилсы
        'has_videos': len(analyzed_reels) > 0,
        'selected_photos': selected_photo_data  # Данные о выбранных фото
    }
    
    # Создаем 10 подробных глав с помощью ИИ
    chapters = {}
    
    # Анализируем пол через ИИ вместо жесткой логики
    print(f"🧠 ИИ анализирует пол для {full_name}...")
    gender_data = analyze_gender_with_ai(full_name, detected_gender)
    
    # Извлекаем данные из ответа ИИ
    gender = gender_data['gender']
    gender_word = gender_data['gender_word']
    she_he = gender_data['she_he']
    her_his = gender_data['her_his']
    love_word = gender_data['love_word']
    
    print(f"✅ ИИ определил: {gender} - будет использовать '{she_he}', '{her_his}'")
    
    # Анализируем реальные посты для контекста
    real_post_analysis = []
    for i, post in enumerate(post_details[:3]):  # Берем первые 3 поста
        post_summary = {
            'caption': post.get('caption', '')[:100] + '...' if len(post.get('caption', '')) > 100 else post.get('caption', ''),
            'location': post.get('location', ''),
            'likes': post.get('likes', 0),
            'type': post.get('type', 'photo')
        }
        real_post_analysis.append(post_summary)
    
    chapter_configs = [
        {
            'key': 'meeting',
            'title': 'Пролог: Первая встреча',
            'prompt': f"""Напиши пролог "Первая встреча" с {full_name} от первого лица (4-5 абзацев). ..."""
        },
        {
            'key': 'first_impression',
            'title': 'Глава первая: Взгляд в душу',
            'prompt': f"""Напиши первую главу "Взгляд в душу" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'world_view',
            'title': 'Глава вторая: Мир через твои глаза',
            'prompt': f"""Напиши вторую главу "Мир через твои глаза" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'memorable_moments',
            'title': 'Глава третья: Мгновения вечности',
            'prompt': f"""Напиши третью главу "Мгновения вечности" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'energy',
            'title': 'Глава четвертая: Энергия и харизма',
            'prompt': f"""Напиши четвёртую главу "Энергия и харизма" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'beauty_style',
            'title': 'Глава пятая: Красота и стиль',
            'prompt': f"""Напиши пятую главу "Красота и стиль" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'mystery',
            'title': 'Глава шестая: Загадка личности',
            'prompt': f"""Напиши шестую главу "Загадка личности" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'influence_on_me',
            'title': 'Глава седьмая: Влияние на меня',
            'prompt': f"""Напиши седьмую главу "Влияние на меня" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'observations',
            'title': 'Глава восьмая: Наблюдения',
            'prompt': f"""Напиши восьмую главу "Наблюдения" о {full_name} (4-5 абзацев). ..."""
        },
        {
            'key': 'gratitude_wishes',
            'title': 'Эпилог: Благодарность и пожелания',
            'prompt': f"""Напиши эпилог "Благодарность и пожелания" для {full_name} (4-5 абзацев). ..."""
        }
    ]
    
    # Генерируем каждую главу через ИИ (БЫСТРО)
    start_time = time.time()
    max_generation_time = 120  # Максимум 2 минуты на всю книгу
    
    # Быстрые fallback тексты для каждой главы
    quick_fallbacks = {
        'meeting': f"Дорогой {full_name}, листая Instagram, я случайно наткнулся на твой профиль. Что-то в твоем взгляде заставило остановиться и изучать каждое фото внимательнее. Возможно, это была искренность, которой так не хватает в мире фильтров. Ты показался мне особенным человеком.",
        
        'first_impression': f"Первое, что поразило в твоем профиле - это естественность. Каждое фото рассказывает историю, а твои глаза особенно выразительны. В них читается ум, доброта и глубина души. Твоя улыбка освещает все вокруг - не наигранная, а настоящая.",
        
        'world_view': f"Больше всего поражает то, как ты видишь мир вокруг себя. У тебя есть дар находить прекрасное в обыденном. Твоя внешность отражает внутренний мир - ты красив естественной красотой, которая не нуждается в прикрасах.",
        
        'memorable_moments': f"Есть кадры, которые врезались в память навсегда. Твоя красота живая, меняющаяся. Твои глаза - отдельная поэма, глубокие и выразительные. Когда ты радуешься, они сияют особым светом. Искренность - твое главное качество.",
        
        'energy': f"В тебе есть особая энергетика, которая чувствуется даже через экран телефона. Умеешь быть собой в любой ситуации. У тебя красивая кожа - здоровая, сияющая. Твои движения полны грации и естественности.",
        
        'beauty_style': f"Красота в твоем случае очевидна для всех. Твое лицо - произведение искусства с правильными пропорциями. У тебя красивые брови, длинные ресницы, безупречная кожа с естественным сиянием.",
        
        'mystery': f"В тебе есть особая загадочность, которая не дает покоя. Каждый кадр открывает что-то новое. Твой взгляд загадочен, в нем есть глубина океана. Должно быть, у тебя красивый голос и грациозная походка.",
        
        'influence_on_me': f"Ты изменил мой взгляд на многие вещи. Стал больше внимания обращать на детали вокруг - игру света, выражения лиц. Ты показал, что красота не требует дорогих декораций. Благодаря тебе понял ценность искренности.",
        
        'observations': f"За время наблюдения сделал интересные открытия. Твое лицо очень фотогеничное, у тебя нет плохих ракурсов. Выразительные руки, которые рассказывают истории. Любишь свет и умело его используешь.",
        
        'gratitude_wishes': f"{full_name}, эта книга подходит к концу, но восхищение остается навсегда. Продолжай быть собой, продолжай фотографировать мир таким, каким ты его видишь. Желаю тебе любви, счастья и ярких моментов. Спасибо за то, что ты есть. Твой поклонник."
    }
    
    for config in chapter_configs:
        # Проверяем, не превысили ли лимит времени
        elapsed_time = time.time() - start_time
        if elapsed_time > max_generation_time:
            print(f"⏰ Превышен лимит времени ({max_generation_time}с), используем быстрые fallback'ы")
            # Заполняем оставшиеся главы быстрыми fallback'ами
            for remaining_config in chapter_configs[len(chapters):]:
                chapters[remaining_config['key']] = quick_fallbacks.get(remaining_config['key'], f"Эта глава о {remaining_config['title'].lower()} написана с особой теплотой и вниманием к деталям.")
            break
        
        try:
            print(f"💝 Генерирую главу '{config['title']}' для {full_name}... ({elapsed_time:.1f}с)")
            
            # Быстрая генерация с таймаутом 15 секунд на главу
            chapter_start = time.time()
            generated_content = generate_memoir_chapter("romantic_book_chapter", {
                'prompt': config['prompt'],
                'context': context_data,
                'style': 'romantic_personal_gift'
            })
            
            chapter_time = time.time() - chapter_start
            if chapter_time > 15:  # Если глава генерировалась дольше 15 секунд
                print(f"⚡ Глава '{config['title']}' генерировалась {chapter_time:.1f}с - долго!")
            
            # Проверяем качество результата
            if len(generated_content.strip()) < 100:  # Если слишком короткий ответ
                print(f"⚡ Короткий ответ для '{config['title']}', использую fallback")
                chapters[config['key']] = quick_fallbacks.get(config['key'], f"Глава о {config['title'].lower()} полна восхищения и теплых слов.")
            else:
                clean_content = strip_cliches(generated_content)
                # Применяем форматирование: абзацы + выделения
                chapters[config['key']] = format_chapter_text(clean_content)
            
            print(f"✅ Глава '{config['title']}' готова за {chapter_time:.1f}с")
            
        except Exception as e:
            print(f"💔 Ошибка генерации главы '{config['title']}': {e}")
            # Быстрый fallback
            chapters[config['key']] = quick_fallbacks.get(config['key'], f"Дорогой {full_name}, эта глава посвящена твоей особенной природе. Ты удивительный человек, и это видно в каждом твоем посте.")
    
    total_time = time.time() - start_time
    print(f"⏱️ Все главы сгенерированы за {total_time:.1f} секунд")
    
    # Генерируем финальное послание
    final_page_content = f"С бесконечным восхищением и благодарностью. Ты — особенный человек. Спасибо тебе за всё."
    try:
        print("💝 Генерирую финальное послание...")
        final_prompt = f"""Напиши очень короткое и поэтичное финальное послание (1 предложения) для романтической книги о {full_name}.

ПОЛ: {gender} - обращайся соответственно.

ИДЕИ:
- "Эта книга — лишь слабая попытка передать твой свет."
- "Спасибо за вдохновение."
- "Пусть твой путь всегда будет прекрасен."

СТИЛЬ: Очень коротко, нежно, искренне. Без длинных вступлений и заключений. Только сама суть.
"""
        final_page_content = generate_memoir_chapter("final_message", {
            'prompt': final_prompt,
            'context': context_data,
            'style': 'poetic_farewell'
        })
        print("✅ Финальное послание готово.")
    except Exception as e:
        print(f"💔 Ошибка генерации финального послания: {e}")
        # fallback is already set
    
    # Генерируем личное название книги
    book_titles = [
        f"Для {full_name} с любовью",
        f"Книга о красоте {full_name}",
        f"Письма {full_name}",
        f"Мои мысли о тебе, {full_name}",
        f"Подарок для {full_name}"
    ]
    book_title = random.choice(book_titles)
    
    # HTML в стиле личного подарка
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Open+Sans:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
    /* Белый фон страниц, чёрный акцент */
    :root {{
        --accent-color: #333333;      /* чёрный вместо фиолетового */
        --background-color: #ffffff;  /* белый фон */
        --text-color: #333;
        --font-body: 'Playfair Display', serif;
        --font-caption: 'Open Sans', sans-serif;
    }}

    @page {{
        size: A5 portrait;
        margin: 2.5cm; /* Еще больше отступы */
        
        @bottom-center {{
            content: counter(page);
            font-family: 'Playfair Display', serif;
            font-size: 16pt;
            color: #555;
            border-top: 1px solid #ddd;
            padding-top: 0.25cm;
            width: 100%;
        }}
    }}

    body {{
        font-family: var(--font-body);
        background-color: var(--background-color) !important;
        color: var(--text-color);
        line-height: 1.6;
        font-size: 24pt;
        margin: 0;
        counter-reset: page;
    }}

    .book-page {{
        page-break-after: always;
        position: relative;
        overflow: hidden;
        background-color: var(--background-color) !important;
        box-shadow: none;  /* убираем тень страниц */
    }}

    .book-page:last-of-type {{
        page-break-after: auto;
    }}

    /* Cover Page */
    .cover-page {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        text-align: center;
    }}

    .cover-title {{
        font-family: 'Playfair Display', serif;
        font-size: 48pt;
        font-weight: 700;
        margin: 0;
    }}

    .cover-subtitle {{
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 24pt;
        margin: 1rem 0 3rem 0;
    }}

    .cover-author {{
        position: absolute;
        bottom: 1.5cm;
        font-size: 18pt;
    }}

    .cover-content {{
        border: 2px solid #333;
        padding: 2rem 3rem;
    }}
    
    .cover-separator {{
        width: 80px;
        height: 1px;
        background: #333;
        margin: 0 auto 1.5rem;
    }}

    .cover-dedication {{
        font-family: 'Open Sans', sans-serif;
        font-style: italic;
        font-size: 14pt;
    }}

    /* Table of Contents */
    .toc-page {{
        padding: 0; /* Padding is handled by @page margins */
    }}

    .toc-title {{
        font-size: 36pt;
        font-weight: bold;
        text-transform: uppercase;
        text-align: center;
        margin-top: 1cm;
        margin-bottom: 2cm;
        color: var(--accent-color);
    }}

    .toc-list {{
        list-style: none;
        padding: 0;
        font-size: 20pt;
        font-family: 'Playfair Display', serif;
    }}

    .toc-item {{
        display: flex;
        margin-bottom: 0.5rem;
        align-items: baseline;
    }}

    .toc-item .chapter-name {{
        order: 1;
        text-decoration: none;
        color: var(--text-color);
    }}
    
    /* Убираем точечные линии-лидеры в оглавлении */
    .toc-item .leader {{
        flex-grow: 0;
        border-bottom: none;
        margin: 0;
        position: static;
    }}

    .toc-item .page-ref {{
        order: 3;
        text-decoration: none;
        color: var(--text-color);
    }}

    .toc-item .page-ref::after {{
        content: target-counter(attr(href), page);
    }}
    
    /* Chapter Page */
    .chapter-page {{
        padding: 0; /* Padding is handled by @page margins */
    }}

    .chapter-main-title {{
        font-family: var(--font-body);
        font-weight: bold;
        font-size: 32pt; /* Немного уменьшил, чтобы помещалось */
        text-align: center;
        text-transform: uppercase;
        color: var(--accent-color);
        margin: 1cm 0;
        line-height: 1.2; /* Добавил высоты строки для многострочных заголовков */
        overflow-wrap: break-word; /* Перенос слишком длинных слов */
        hyphens: auto; /* Автоматические переносы */
    }}
    
    .chapter-subtitle {{
        font-family: var(--font-body);
        font-style: italic;
        font-size: 18pt;
        text-align: left;
        margin: 0 0 1rem 0;
    }}

    .chapter-image-container {{
        text-align: center;
        margin: 1cm 0;
        page-break-inside: avoid;
    }}

    .chapter-image {{
        max-width: 90%;
        border: 1px solid #ddd;
        padding: 0.5cm;
    }}

    .chapter-image-caption {{
        font-family: var(--font-caption);
        font-style: italic;
        font-size: 14pt;
        margin-top: 0.5rem;
        color: var(--accent-color);
    }}
    
    .chapter-body p {{
        font-size: 24pt;
        line-height: 1.6;
        margin-bottom: 1em;
    }}

    .chapter-body p:first-of-type::first-letter {{
        /* Современный способ создания буквицы, который лучше поддерживается рендерами PDF */
        initial-letter: 3; /* Буква будет высотой в 3 строки */
        font-weight: bold;
        padding-right: 0.2em; /* Небольшой отступ справа для воздуха */
        color: #555; /* Сделаем ее чуть светлее для элегантности */
    }}
    
    /* Final Page Styles */
    .final-page {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }}
    .final-content {{
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 24pt;
        line-height: 1.7;
        max-width: 80%;
    }}
    .final-ornament {{
        font-size: 32pt;
        color: var(--accent-color);
        margin: 2rem 0;
        font-family: serif;
    }}
    .final-signature {{
        margin-top: 1rem;
        font-size: 18pt;
        font-style: normal;
    }}

    @media screen {{
        body {{
            font-size: 16px;
        }}
        .book-page {{
            width: 148mm; /* A5 width */
            min-height: 210mm; /* A5 height */
            margin: 2rem auto;
            padding: 2.5cm; /* Увеличенные отступы для веб-просмотра */
            box-sizing: border-box;
            height: auto;
        }}
        .cover-page {{
            height: 210mm;
            position: relative;
        }}
        .chapter-body p {{ font-size: 14pt; }}
        .chapter-body p:first-of-type::first-letter {{ font-size: 38pt; }}
        .cover-title {{ font-size: 32pt; }}
        .cover-subtitle {{ font-size: 18pt; }}
        .toc-title {{ font-size: 24pt; }}
        .toc-list {{ font-size: 14pt; }}
        .chapter-main-title {{ font-size: 24pt; }}
        .chapter-subtitle {{ font-size: 12pt; }}
        .final-content {{ font-size: 18pt; }}
        .final-signature {{ font-size: 14pt; }}
    }}
    </style>
</head>
<body>

<!-- Cover Page -->
<div class="book-page cover-page">
    <div class="cover-content">
        <h1 class="cover-title">{full_name.upper()}</h1>
        <p class="cover-subtitle">An Unforgettable Story</p>
        <div class="cover-separator"></div>
        <p class="cover-dedication">A gift from a secret admirer</p>
    </div>
</div>

<!-- Table of Contents -->
<div class="book-page toc-page">
    <h2 class="toc-title">Table of Contents</h2>
    <ul class="toc-list">
        {"".join([f'''
            <li class="toc-item">
                <a href="#chapter-{config['key']}" class="chapter-name">Chapter {i+1} – {config['title']}</a>
                <span class="leader"></span>
                <a href="#chapter-{config['key']}" class="page-ref"></a>
            </li>
        ''' for i, config in enumerate(chapter_configs)])}
    </ul>
</div>

<!-- Chapter Pages -->
chapter_html_list = []
for i, config in enumerate(chapter_configs):
    if i < len(selected_photo_data):
        # Извлекаем данные фото в отдельные переменные
        photo_image = selected_photo_data[i]["image"]
        photo_analysis = selected_photo_data[i]["analysis"]
        truncated_analysis = photo_analysis[:80] + "..." if len(photo_analysis) > 80 else photo_analysis
        
        image_block = (
            f'<div class="chapter-image-container">'
            f'<img src="{photo_image}" alt="Photo for Chapter {i+1}" class="chapter-image">'
            f'<p class="chapter-image-caption">'
            f'{truncated_analysis}'
            f'</p></div>'
        )
    else:
        image_block = ""
    
    # Подготавливаем fallback текст для главы
    fallback_text = f'<p>{config["title"]} о {full_name} — это всегда повод для улыбки!</p>'
    
    chapter_html_list.append(
        f'''
        <div id="chapter-{config['key']}" class="book-page chapter-page">
            <h3 class="chapter-subtitle">{config['title']}</h3>
            <h2 class="chapter-main-title">{config['title']}</h2>
            {image_block}
            <div class="chapter-body">
                {chapters.get(config['key'], fallback_text)}
            </div>
        </div>
        '''
    )
chapters_html = "".join(chapter_html_list)
final_page_content_html = final_page_content.replace('\n', '<br>')

<!-- Final Page -->
<div class="book-page final-page">
    <div class="final-content">
        <p>{final_page_content_html}</p>
    </div>
    <div class="final-ornament">
        ✦
    </div>
    <div class="final-signature">
        <p>Пусть твоя история вдохновляет других.</p>
    </div>
</div>

</body>
</html>"""
    
    return html


def create_pdf_with_weasyprint(output_path: Path, html_content: str):
    """Генерирует красивый PDF из HTML используя WeasyPrint."""
    try:
        from weasyprint import HTML, CSS
        
        # Создаем PDF из HTML контента
        html_doc = HTML(string=html_content)
        
        # Дополнительные CSS стили для печати PDF
        print_css = CSS(string="""
            @page {
                margin: 1.5cm;
                size: A4;
            }
            
            body {
                margin: 0;
                padding: 0;
            }
            
            .memoir-page {
                page-break-after: always;
                margin: 0;
                box-shadow: none;
            }
            
            .memoir-page:last-child {
                page-break-after: auto;
            }
            
            .photo-frame {
                box-shadow: none;
                border: 1px solid #ddd;
            }
            
            /* Убираем лишние тени для печати */
            * {
                -webkit-print-color-adjust: exact !important;
                color-adjust: exact !important;
            }
        """)
        
        # Генерируем PDF
        html_doc.write_pdf(str(output_path), stylesheets=[print_css])
        print(f"✅ Красивый PDF создан с помощью WeasyPrint: {output_path}")
        
    except ImportError:
        print("❌ WeasyPrint не установлен. Устанавливаю...")
        import subprocess
        import sys
        
        try:
            # Пытаемся установить weasyprint
            subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
            print("✅ WeasyPrint установлен успешно")
            
            # Повторяем попытку создания PDF
            from weasyprint import HTML, CSS
            html_doc = HTML(string=html_content)
            print_css = CSS(string="""
                @page {
                    margin: 1.5cm;
                    size: A4;
                }
                
                body {
                    margin: 0;
                    padding: 0;
                }
                
                .memoir-page {
                    page-break-after: always;
                    margin: 0;
                    box-shadow: none;
                }
                
                .memoir-page:last-child {
                    page-break-after: auto;
                }
                
                .photo-frame {
                    box-shadow: none;
                    border: 1px solid #ddd;
                }
                
                * {
                    -webkit-print-color-adjust: exact !important;
                    color-adjust: exact !important;
                }
            """)
            
            html_doc.write_pdf(str(output_path), stylesheets=[print_css])
            print(f"✅ Красивый PDF создан с помощью WeasyPrint: {output_path}")
            
        except Exception as install_error:
            print(f"❌ Не удалось установить WeasyPrint: {install_error}")
            # Fallback к простому PDF
            create_simple_pdf_fallback(output_path)
            
    except Exception as e:
        print(f"❌ Ошибка при создании PDF с WeasyPrint: {e}")
        # Fallback к простому PDF
        create_simple_pdf_fallback(output_path)

def create_simple_pdf_fallback(output_path: Path):
    """Простой fallback PDF если WeasyPrint недоступен."""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        
        try:
            pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
            pdf.set_font('DejaVu', '', 12)
        except:
            pdf.set_font('Arial', '', 12)
        
        pdf.cell(0, 20, "Романтическая книга", 0, 1, 'C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, "PDF создан в упрощенном режиме. Для красивого PDF установите WeasyPrint.")
        
        pdf.output(str(output_path))
        print(f"✅ Создан простой PDF (fallback): {output_path}")
        
    except Exception as fallback_error:
        print(f"❌ Ошибка создания fallback PDF: {fallback_error}")

def create_pdf_with_fpdf(output_path: Path, chapters: dict, analysis: dict, images: list[Path]):
    """(DEPRECATED) Старая функция создания PDF. Используйте create_pdf_with_weasyprint."""
    print("⚠️ create_pdf_with_fpdf deprecated. WeasyPrint создаст более красивый PDF.")
    create_simple_pdf_fallback(output_path)

def create_pdf_from_html(html_content: str, output_path: Path) -> Path:
    """(DEPRECATED) Генерирует PDF из HTML контента"""
    print("⚠️ create_pdf_from_html is deprecated. Use create_pdf_with_weasyprint.")
    return output_path

async def create_pdf_from_html_async(html_path: Path, output_path: Path) -> Path:
    """(DEPRECATED) Асинхронно генерирует PDF из HTML файла."""
    print("⚠️ create_pdf_from_html_async is deprecated and will be removed. Use create_pdf_with_weasyprint.")
    # Оставляем заглушку, чтобы не ломать вызовы, но она ничего не делает
    # В идеале, нужно переключить все вызовы на новый метод
    return output_path

def format_chapter_text(text: str) -> str:
    """Очищает и форматирует текст главы."""
    # Сначала разбиваем текст на параграфы по переносам строк
    paragraphs = text.strip().split('\n')
    
    highlight_words = [
        'люблю', 'восхищаюсь', 'красота', 'улыбка', 'вдохновение', 'нежность', 'счастье',
        'особый', 'магия', 'мечта', 'свет', 'душа', 'сердце', 'навсегда', 'благодарю',
        'ты', 'твой', 'твоя', 'тебя', 'мир', 'жизнь', 'чувства', 'эмоции', 'вдохновляешь',
        'улыбка', 'глаза', 'взгляд', 'обожаю', 'нежно', 'искренне', 'светишься', 'особенная', 'особенный'
    ]
    pattern = re.compile(r'\\b(' + '|'.join(highlight_words) + r')\\b', re.IGNORECASE)

    # Ограничиваем количество выделений
    bold_count = 0
    max_bold = 3

    def highlight(match):
        nonlocal bold_count
        if bold_count < max_bold:
            bold_count += 1
            # Возвращаем слово в теге <b>
            return f'<b>{match.group(1)}</b>'
        # Если лимит исчерпан, возвращаем слово без изменений
        return match.group(1)

    formatted_paragraphs = []
    for p in paragraphs:
        if p.strip():
            # Применяем выделение к каждому параграфу с ограничением
            highlighted_p = pattern.sub(highlight, p)
            formatted_paragraphs.append(f'<p>{highlighted_p}</p>')
            
    return "".join(formatted_paragraphs)

# --- НОВЫЙ КОД ОТ БРАТА ---
import re
# Правильный импорт АСИНХРОННОГО клиента
from app.services.llm_client import async_client, settings


async def generate_text_pages(run_id: str, style: str,
                              image_names: list[str],
                              raw_comments: list[str]) -> list[str]:
    """
    Генерирует связный, личный рассказ для флипбука, анализируя профиль.
    """
    # 1. Загружаем и анализируем данные профиля
    posts_json_path = Path("data") / run_id / "posts.json"
    if not posts_json_path.exists():
        raise ValueError(f"posts.json не найден для {run_id}")
    
    posts_data = json.loads(posts_json_path.read_text(encoding="utf-8"))
    profile_analysis = analyze_profile_data(posts_data)

    full_name = profile_analysis.get('full_name') or profile_analysis.get('username') or "этого человека"

    # 2. Создаем мощный и подробный промпт
    system_prompt = f"""
Ты — профессиональный сценарист и романтический писатель. Твоя задача — создать связный и эмоциональный рассказ для флипбук-альбома.
Ты получишь данные о профиле в Instagram и список изображений.

Создай книгу из 5 частей (пролог + 3 главы + эпилог), используя максимум 5 изображений:

1. **Пролог** (первое изображение) - знакомство с героем
2. **Глава первая** (второе изображение) - начало истории
3. **Глава вторая** (третье изображение) - развитие сюжета
4. **Глава третья** (четвертое изображение) - кульминация
5. **Эпилог** (пятое изображение) - финал и благодарность

Для каждой части напиши 120–150 слов (3–4 коротких абзаца).
Обращайся к человеку на «ты», избегай повторов и клише.
Текст для каждой страницы должен быть связан с предыдущим, создавая единое повествование о человеке по имени {full_name}.
Используй информацию из `profile_data` и `raw_comments`, чтобы текст был личным, а не общим.
Добавляй пословицы и мудрые изречения в каждую главу.

Выдавай _только_ JSON в таком формате:
{{
  "prologue": "Текст пролога...",
  "pages": [
    "Текст для первой главы...",
    "Текст для второй главы...", 
    "Текст для третьей главы...",
    "Текст для эпилога..."
  ]
}}

Количество элементов в массиве "pages" должно быть равно 4 (3 главы + эпилог).
Не добавляй ничего лишнего. Только JSON.
    """.strip()

    user_prompt_data = {
        "profile_data": {
            "full_name": profile_analysis.get('full_name', ''),
            "username": profile_analysis.get('username', ''),
            "bio": profile_analysis.get('bio', '')
        },
        "images": image_names[:5],  # Ограничиваем до 5 изображений
        "raw_comments": raw_comments
    }

    # 3. Вызываем LLM с новым промптом
    resp = await async_client.chat.completions.create(
        model=settings.AZURE_OPENAI_GPT4_DEPLOYMENT, # gpt-4.1-mini используется под этим deployment name
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt_data, ensure_ascii=False)}
        ],
        temperature=0.7,
        max_tokens=4000, # Увеличим для более длинных текстов
    )
    raw = resp.choices[0].message.content.strip()

    # 4. Парсим JSON с фолбэком на regex
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️ LLM-ответ не является валидным JSON, пытаюсь извлечь regex-ом:\\n{raw}")
        match = re.search(r"\\{[\s\S]*\\}", raw)
        if match:
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError:
                 raise ValueError(f"Не удалось распарсить JSON даже после regex: {match.group(0)}")
        else:
            raise ValueError(f"В ответе LLM не найден JSON-объект: {raw}")

    prologue = payload.get("prologue")
    pages = payload.get("pages")
    if not prologue or not isinstance(prologue, str) or not isinstance(pages, list) or not pages or not all(isinstance(p, str) for p in pages):
        raise ValueError(f"JSON-ответ от LLM не содержит корректного 'prologue' и списка 'pages': {payload}")

    # Проверяем, что количество страниц совпадает
    if len(pages) != 4:  # 3 главы + эпилог
        print(f"⚠️ ВНИМАНИЕ: LLM вернул {len(pages)} страниц, а ожидалось 4 (3 главы + эпилог). Тексты могут не соответствовать структуре.")

    return [prologue] + pages


# --- КОНЕЦ НОВОГО КОДА ---

def build_fantasy_book(run_id: str, images: list[Path], texts: str, book_format: str = "classic", user_id: str = None):
    """Создание HTML фэнтези-книги"""
    try:
        run_dir = Path("data") / run_id
        posts_json = run_dir / "posts.json"
        images_dir = run_dir / "images"

        if posts_json.exists():
            posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
        else:
            posts_data = []

        analysis = analyze_profile_data(posts_data)
        username = analysis.get("username", "...")

        actual_images = []
        if images_dir.exists():
            for img_file in sorted(images_dir.glob("*")):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    actual_images.append(img_file)

        # Если формат classic — используем новую функцию с 10 главами
        if book_format == "classic":
            from app.styles.fantasy import generate_classic_fantasy_book
            html = generate_classic_fantasy_book(run_id, actual_images, texts, user_id)
        else:
            # Старый вариант (5 глав)
            content = {"format": "fantasy"}
            html = create_fantasy_instagram_book_html(content, analysis, actual_images)

        out = Path("data") / run_id
        out.mkdir(parents=True, exist_ok=True)

        html_file = out / "book.html"
        html_file.write_text(html, encoding="utf-8")

        # Генерируем PDF версию
        try:
            pdf_file = out / "book.pdf"
            create_pdf_with_weasyprint(pdf_file, html)
            print(f"📄 Фэнтези PDF версия создана: {pdf_file}")
        except Exception as pdf_error:
            print(f"❌ Ошибка создания PDF: {pdf_error}")

        # Автоматическое сохранение в библиотеку пользователя
        if user_id:
            try:
                import uuid
                import datetime
                import shutil
                profile_username = analysis.get("username")
                profile_full_name = analysis.get("full_name")
                book_id = str(uuid.uuid4())
                title = f"Летопись для {profile_full_name or profile_username or 'Неизвестный'}"
                def get_user_books_db_path_local(user_id: str) -> Path:
                    user_books_dir = Path("data") / "user_books"
                    user_books_dir.mkdir(parents=True, exist_ok=True)
                    return user_books_dir / f"{user_id}.json"
                def load_user_books_local(user_id: str) -> list[dict]:
                    books_file = get_user_books_db_path_local(user_id)
                    if not books_file.exists():
                        return []
                    try:
                        return json.loads(books_file.read_text(encoding="utf-8"))
                    except:
                        return []
                def save_user_books_local(user_id: str, books: list[dict]):
                    books_file = get_user_books_db_path_local(user_id)
                    books_file.write_text(json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8")
                def copy_book_to_user_library_local(run_id: str, user_id: str, book_id: str) -> bool:
                    try:
                        source_dir = Path("data") / run_id
                        user_library_dir = Path("data") / "user_books" / user_id / book_id
                        user_library_dir.mkdir(parents=True, exist_ok=True)
                        for file in ["book.html", "book.pdf", "posts.json"]:
                            source_file = source_dir / file
                            if source_file.exists():
                                shutil.copy2(source_file, user_library_dir / file)
                        source_images = source_dir / "images"
                        if source_images.exists():
                            target_images = user_library_dir / "images"
                            if target_images.exists():
                                shutil.rmtree(target_images)
                            shutil.copytree(source_images, target_images)
                        return True
                    except Exception as e:
                        print(f"Ошибка копирования книги {run_id} для пользователя {user_id}: {e}")
                        return False
                books = load_user_books_local(user_id)
                already_saved = False
                for book in books:
                    if book["run_id"] == run_id:
                        already_saved = True
                        break
                if not already_saved:
                    if copy_book_to_user_library_local(run_id, user_id, book_id):
                        new_book = {
                            "id": book_id,
                            "run_id": run_id,
                            "title": title,
                            "created_at": datetime.datetime.now().isoformat(),
                            "profile_username": profile_username,
                            "profile_full_name": profile_full_name,
                            "has_pdf": pdf_file.exists(),
                            "has_html": html_file.exists()
                        }
                        books.append(new_book)
                        save_user_books_local(user_id, books)
                        print(f"📚 Книга автоматически сохранена в библиотеку пользователя {user_id}")
                    else:
                        print("❌ Ошибка автоматического сохранения книги в библиотеку")
                else:
                    print("📚 Книга уже была сохранена в библиотеке пользователя")
            except Exception as save_error:
                print(f"❌ Ошибка автоматического сохранения: {save_error}")
        final_messages = [
            f"Судьба свершилась! Фэнтези-книга о @{username} готова к прочтению: {html_file}",
            f"Ваша персональная летопись создана! @{username}, вы теперь — герой саги: {html_file}",
            f"Хроника приключений @{username} завершена! Каждая страница наполнена магией: {html_file}",
            f"Книга-эпос @{username} готова! В ней живёт дух древних легенд: {html_file}"
        ]
        print(random.choice(final_messages))
    except Exception as e:
        print(f"Ошибка при создании фэнтези-книги о @{username}: {e}")
        try:
            basic_html = f"""
            <html>
            <head>
                <title>Фэнтези-книга</title>
                <style>
                    body {{ background: #f5f3e7; font-family: serif; padding: 20px; }}
                    .error {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Фэнтези-книга</h1>
                    <p>Извините, произошла ошибка при создании книги: {e}</p>
                    <p>Попробуйте еще раз позже</p>
                </div>
            </body>
            </html>
            """
            html_file = Path("data") / run_id / "book.html"
            html_file.write_text(basic_html, encoding="utf-8")
        except Exception as final_error:
            print(f"Критическая ошибка: {final_error}")

def create_fantasy_instagram_book_html(content: dict, analysis: dict, images: list[Path]) -> str:
    """Создает HTML фэнтези-книгу в стиле возвышенной личной фантастики, как в примере пользователя."""
    import random, time
    from app.services.llm_client import strip_cliches
    full_name = analysis.get('full_name', analysis.get('username', 'герой древних хроник'))
    username = analysis.get('username', 'hero')
    followers = analysis.get('followers', 0)
    posts_count = analysis.get('posts_count', 0)
    bio = analysis.get('bio', '')
    post_details = analysis.get('post_details', []) if 'post_details' in analysis else []
    real_captions = [p.get('caption', '') for p in post_details[:5] if p.get('caption')]
    locations = [p.get('location', '') for p in post_details[:3] if p.get('location')]
    processed_images = []
    selected_photo_data = []
    detected_gender = "unknown"
    if images:
        total_images = len(images)
        if total_images >= 10:
            selected_indices = random.sample(range(total_images), 10)
            selected_indices.sort()
        elif total_images >= 5:
            selected_indices = list(range(total_images))
            while len(selected_indices) < 10:
                random_idx = random.randint(0, total_images - 1)
                selected_indices.append(random_idx)
        else:
            selected_indices = []
            for _ in range(10):
                random_idx = random.randint(0, total_images - 1)
                selected_indices.append(random_idx)
        for i, idx in enumerate(selected_indices):
            img_path = images[idx]
            if img_path.exists():
                try:
                    from PIL import Image, ImageEnhance
                    from io import BytesIO
                    import base64
                    with Image.open(img_path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        max_size = (700, 500)
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(1.05)
                        enhancer = ImageEnhance.Color(img)
                        img = enhancer.enhance(1.1)
                        buffer = BytesIO()
                        img.save(buffer, format='JPEG', quality=90)
                        img_str = base64.b64encode(buffer.getvalue()).decode()
                        processed_images.append(f"data:image/jpeg;base64,{img_str}")
                        fallback_descriptions = [
                            "Взгляд, в котором отражается древняя магия",
                            "Аура героя, сияющая сквозь века",
                            "Сила стихий в каждом движении",
                            "Тайна, скрытая за улыбкой",
                            "Мудрость древних в глазах",
                            "Союзник драконов и духов",
                            "Печать судьбы на челе героя",
                            "Свет, что ведёт сквозь тьму",
                            "Тёплый кристалл мыслей",
                            "Завет света в каждом взгляде"
                        ]
                        selected_photo_data.append({
                            'index': idx + 1,
                            'analysis': fallback_descriptions[i % len(fallback_descriptions)],
                            'image': f"data:image/jpeg;base64,{img_str}"
                        })
                except Exception as e:
                    print(f"❌ Ошибка обработки изображения {img_path}: {e}")
    def get_safe_photo_analysis(index: int, fallback_text: str) -> str:
        if not selected_photo_data:
            return fallback_text
        safe_index = index % len(selected_photo_data)
        return selected_photo_data[safe_index]['analysis']
    context_data = {
        'full_name': full_name,
        'username': username
    }
    # Темы глав и стиль — как в примере пользователя
    chapter_configs = [
        {'key': 'destiny_bell', 'title': 'Пролог: Звон Судьбы', 'prompt': f"Напиши пролог (1-2 абзаца, 80-120 слов) с заголовком 'Звон Судьбы' о человеке по имени {full_name}. Стиль — возвышенная фантастика про личность, как будто ты пишешь личное письмо герою. Используй метафоры света, судьбы, внутренней силы, но не уходи в сказку. Пиши лично, с эмоциями, как будто обращаешься к герою. Добавь пословицу: 'Судьба зовет тех, кто готов услышать её зов'. Не повторяй пример, но держи такой же стиль, как в образце пользователя."},
        {'key': 'primordial_sparks', 'title': 'Глава первая: Искры Первоначала', 'prompt': f"Напиши первую главу (1-2 абзаца, 80-120 слов) с заголовком 'Искры Первоначала' о {full_name}. Стиль — возвышенная фантастика про личность, метафоры света, силы, внутреннего пробуждения. Пиши лично, с эмоциями, не повторяя пример, но в том же стиле. Добавь пословицу: 'Из искры возгорится пламя, из мечты родится судьба'. Пиши как главу эпического романа."},
        {'key': 'ancient_whisper', 'title': 'Глава вторая: Шепот Древних', 'prompt': f"Напиши вторую главу (1-2 абзаца, 80-120 слов) с заголовком 'Шепот Древних' о {full_name}. Стиль — возвышенная фантастика про личность, метафоры времени, памяти, внутренней мудрости. Пиши лично, с эмоциями, не повторяя пример, но в том же стиле. Добавь пословицу: 'Мудрость древних живет в сердцах достойных'. Пиши как главу эпического романа."},
        {'key': 'flame_of_memory', 'title': 'Глава третья: Пламя Памяти', 'prompt': f"Напиши третью главу (1-2 абзаца, 80-120 слов) с заголовком 'Пламя Памяти' о {full_name}. Стиль — возвышенная фантастика про личность, метафоры огня, воспоминаний, внутренней силы. Пиши лично, с эмоциями, не повторяя пример, но в том же стиле. Добавь пословицу: 'Пламя прошлого освещает путь в будущее'. Пиши как главу эпического романа."},
        {'key': 'epilogue', 'title': 'Эпилог: Завет Света', 'prompt': f"Напиши эпилог (1-2 абзаца, 80-120 слов) с заголовком 'Завет Света' — итоговые мысли и пожелания для {full_name}. Стиль — возвышенная фантастика про личность, метафоры света, надежды, будущего. Пиши лично, с эмоциями, не повторяя пример, но в том же стиле. Добавь пословицу: 'Свет, что ты несешь, осветит путь другим'. Пиши как финальную главу эпического романа."},
    ]
    try:
        fantasy_book = run_fantasy_book_agent_sync([
            {
                'key': c['key'],
                'title': c['title'],
                'prompt': c['prompt']
            } for c in chapter_configs
        ], context_data, {})
        chapters = {chapter.key: chapter.text for chapter in fantasy_book.chapters}
        final_page_content = fantasy_book.final_message
        book_title = fantasy_book.title
    except Exception:
        chapters = {c['key']: '' for c in chapter_configs}
        final_page_content = "Пусть твоя сага будет вечной, а имя — вписано в Книгу Героев!"
        book_title = f"Хроники {full_name}"
    html = """<!DOCTYPE html>
<html lang=\"ru\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{book_title}</title>
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Crimson+Text:ital,wght@0,400;0,700;1,400&display=swap\" rel=\"stylesheet\">
    <style>
    :root {{
        --accent-color: #222;
        --background-color: #fff;
        --text-color: #222;
        --font-body: 'Crimson Text', serif;
        --font-caption: 'Cinzel', serif;
    }}
    @page {{
        size: A5 portrait;
        margin: 2.5cm;
        @bottom-center {{
            content: counter(page);
            font-family: 'Cinzel', serif;
            font-size: 14pt;
            color: #555;
            border-top: 1px solid #ddd;
            padding-top: 0.25cm;
            width: 100%;
        }}
    }}
    body {{
        font-family: var(--font-body);
        background-color: var(--background-color) !important;
        color: var(--text-color);
        line-height: 1.6;
        font-size: 20pt;
        margin: 0;
        counter-reset: page;
    }}
    .book-page {{
        page-break-after: always;
        position: relative;
        overflow: hidden;
        background-color: var(--background-color) !important;
        box-shadow: none;
    }}
    .book-page:last-of-type {{
        page-break-after: auto;
    }}
    .cover-page {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        text-align: center;
    }}
    .cover-title {{
        font-family: 'Cinzel', serif;
        font-size: 40pt;
        font-weight: 700;
        margin: 0;
    }}
    .cover-subtitle {{
        font-family: 'Cinzel', serif;
        font-style: italic;
        font-size: 20pt;
        margin: 1rem 0 3rem 0;
    }}
    .cover-content {{
        border: none;
        padding: 2rem 3rem;
    }}
    .cover-separator {{
        width: 80px;
        height: 1px;
        background: #222;
        margin: 0 auto 1.5rem;
    }}
    .cover-dedication {{
        font-family: 'Crimson Text', serif;
        font-style: italic;
        font-size: 12pt;
    }}
    .toc-title {{
        font-size: 28pt;
        font-weight: bold;
        text-transform: uppercase;
        text-align: center;
        margin-top: 1cm;
        margin-bottom: 2cm;
        color: var(--accent-color);
    }}
    .toc-list {{
        list-style: none;
        padding: 0;
        font-size: 16pt;
        font-family: 'Cinzel', serif;
    }}
    .toc-item {{
        display: flex;
        margin-bottom: 0.5rem;
        align-items: baseline;
    }}
    .toc-item .chapter-name {{
        order: 1;
        text-decoration: none;
        color: var(--text-color);
    }}
    .toc-item .leader {{
        flex-grow: 0;
        border-bottom: none;
        margin: 0;
        position: static;
    }}
    .toc-item .page-ref {{
        order: 3;
        text-decoration: none;
        color: var(--text-color);
    }}
    .chapter-page {{
        padding: 0;
    }}
    .chapter-main-title {{
        font-family: var(--font-body);
        font-weight: bold;
        font-size: 24pt;
        text-align: center;
        text-transform: uppercase;
        color: var(--accent-color);
        margin: 1cm 0;
        line-height: 1.2;
        overflow-wrap: break-word;
        hyphens: auto;
    }}
    .chapter-subtitle {{
        font-family: var(--font-body);
        font-style: italic;
        font-size: 14pt;
        text-align: left;
        margin: 0 0 1rem 0;
    }}
    .chapter-image-container {{
        text-align: center;
        margin: 1cm 0;
        page-break-inside: avoid;
    }}
    .chapter-image {{
        max-width: 90%;
        border: none;
        padding: 0.5cm;
    }}
    .chapter-image-caption {{
        font-family: var(--font-caption);
        font-style: italic;
        font-size: 12pt;
        margin-top: 0.5rem;
        color: var(--accent-color);
    }}
    .chapter-body p {{
        font-size: 20pt;
        line-height: 1.6;
        margin-bottom: 1em;
    }}
    .chapter-body p:first-of-type::first-letter {{
        initial-letter: 2;
        font-weight: bold;
        padding-right: 0.2em;
        color: #555;
    }}
    .final-page {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }}
    .final-content {{
        font-family: 'Cinzel', serif;
        font-style: italic;
        font-size: 20pt;
        line-height: 1.7;
        max-width: 80%;
    }}
    .final-ornament {{
        font-size: 28pt;
        color: var(--accent-color);
        margin: 2rem 0;
        font-family: serif;
    }}
    .final-signature {{
        margin-top: 1rem;
        font-size: 14pt;
        font-style: normal;
    }}
    @media screen {{
        body {{ font-size: 12px; }}
        .book-page {{ width: 148mm; min-height: 210mm; margin: 2rem auto; padding: 2.5cm; box-sizing: border-box; height: auto; }}
        .cover-page {{ height: 210mm; position: relative; }}
        .chapter-body p {{ font-size: 12pt; }}
        .chapter-body p:first-of-type::first-letter {{ font-size: 28pt; }}
        .cover-title {{ font-size: 24pt; }}
        .cover-subtitle {{ font-size: 14pt; }}
        .toc-title {{ font-size: 18pt; }}
        .toc-list {{ font-size: 12pt; }}
        .chapter-main-title {{ font-size: 16pt; }}
        .chapter-subtitle {{ font-size: 10pt; }}
        .final-content {{ font-size: 12pt; }}
        .final-signature {{ font-size: 10pt; }}
    }}
    </style>
</head>
<body>
<!-- Cover Page -->
<div class="book-page cover-page">
    <div class="cover-content">
        <h1 class="cover-title">{full_name.upper()}</h1>
        <p class="cover-subtitle">Фантастическая история личности</p>
        <div class="cover-separator"></div>
        <p class="cover-dedication">A tale of inner power and destiny</p>
    </div>
</div>
<!-- Table of Contents -->
<div class="book-page toc-page">
    <h2 class="toc-title">Содержание</h2>
    <ul class="toc-list">
        {"".join([f'''
            <li class="toc-item">
                <a href="#chapter-{config['key']}" class="chapter-name">Глава {i+1} – {config['title']}</a>
                <span class="leader"></span>
                <a href="#chapter-{config['key']}" class="page-ref"></a>
            </li>
        ''' for i, config in enumerate(chapter_configs)])}
    </ul>
</div>
<!-- Chapter Pages -->
{chapters_html}
<!-- Final Page -->
<div class="book-page final-page">
    <div class="final-content">
        <p>{final_page_content_html}</p>
    </div>
    <div class="final-ornament">
        ✦
    </div>
    <div class="final-signature">
        <p>Пусть твоя история вдохновляет других.</p>
    </div>
</div>
</body>
</html>"""
    return html

def build_humor_book(run_id: str, images: list[Path], texts: str, book_format: str = "classic", user_id: str = None):
    """Создание HTML юмористической книги"""
    try:
        run_dir = Path("data") / run_id
        posts_json = run_dir / "posts.json"
        images_dir = run_dir / "images"
        if posts_json.exists():
            posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
        else:
            posts_data = []
        analysis = analyze_profile_data(posts_data)
        username = analysis.get("username", "...")
        actual_images = []
        if images_dir.exists():
            for img_file in sorted(images_dir.glob("*")):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    actual_images.append(img_file)
        # Если формат classic — используем новую функцию
        if book_format == "classic":
            html = create_classic_humor_book_html({}, analysis, actual_images)
        else:
            # Юмористические сообщения о процессе анализа
            humor_analysis_messages = [
                f"Изучаю профиль @{username} с улыбкой... Каждый пост — потенциальная шутка!",
                f"Анализирую чувство юмора @{username}... Готовлюсь к стендапу!",
                f"Читаю посты @{username} как комедийный сценарий... Смех гарантирован!",
                f"Изучаю стиль @{username} — готовлюсь к юмористическому шоу!",
                f"Анализирую характер @{username} через призму юмора... Будет весело!"
            ]
            humor_photo_messages = [
                f"Собираю {len(actual_images)} забавных кадров для комедийного альбома...",
                f"Каждое из {len(actual_images)} фото — материал для стендапа!",
                f"Готовлю {len(actual_images)} кадров для юмористического шоу!",
                f"{len(actual_images)} фотографий — источник вдохновения для комедии!",
                f"Архивирую {len(actual_images)} моментов для весёлой истории!"
            ]
            print(random.choice(humor_analysis_messages))
            print(random.choice(humor_photo_messages))
            from app.styles.humor import generate_humor_chapters, create_humor_html
            chapters = generate_humor_chapters(analysis, actual_images)
            html = create_humor_html(analysis, chapters, actual_images)
        out = Path("data") / run_id
        out.mkdir(parents=True, exist_ok=True)
        html_file = out / "book.html"
        html_file.write_text(html, encoding="utf-8")
        # Генерируем PDF версию
        try:
            pdf_file = out / "book.pdf"
            create_pdf_with_weasyprint(pdf_file, html)
            print(f"📄 Юмористическая PDF версия создана: {pdf_file}")
        except Exception as pdf_error:
            print(f"❌ Ошибка создания PDF: {pdf_error}")
        # Автоматическое сохранение в библиотеку пользователя
        if user_id:
            try:
                import uuid
                import datetime
                import shutil
                profile_username = analysis.get("username")
                profile_full_name = analysis.get("full_name")
                book_id = str(uuid.uuid4())
                title = f"Весёлые истории о {profile_full_name or profile_username or 'Неизвестный'}"
                def get_user_books_db_path_local(user_id: str) -> Path:
                    user_books_dir = Path("data") / "user_books"
                    user_books_dir.mkdir(parents=True, exist_ok=True)
                    return user_books_dir / f"{user_id}.json"
                def load_user_books_local(user_id: str) -> list[dict]:
                    books_file = get_user_books_db_path_local(user_id)
                    if not books_file.exists():
                        return []
                    try:
                        return json.loads(books_file.read_text(encoding="utf-8"))
                    except:
                        return []
                def save_user_books_local(user_id: str, books: list[dict]):
                    books_file = get_user_books_db_path_local(user_id)
                    books_file.write_text(json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8")
                def copy_book_to_user_library_local(run_id: str, user_id: str, book_id: str) -> bool:
                    try:
                        source_dir = Path("data") / run_id
                        user_library_dir = Path("data") / "user_books" / user_id / book_id
                        user_library_dir.mkdir(parents=True, exist_ok=True)
                        for file in ["book.html", "book.pdf", "posts.json"]:
                            source_file = source_dir / file
                            if source_file.exists():
                                shutil.copy2(source_file, user_library_dir / file)
                        source_images = source_dir / "images"
                        if source_images.exists():
                            target_images = user_library_dir / "images"
                            if target_images.exists():
                                shutil.rmtree(target_images)
                            shutil.copytree(source_images, target_images)
                        return True
                    except Exception as e:
                        print(f"Ошибка копирования книги {run_id} для пользователя {user_id}: {e}")
                        return False
                books = load_user_books_local(user_id)
                already_saved = False
                for book in books:
                    if book["run_id"] == run_id:
                        already_saved = True
                        break
                if not already_saved:
                    if copy_book_to_user_library_local(run_id, user_id, book_id):
                        new_book = {
                            "id": book_id,
                            "run_id": run_id,
                            "title": title,
                            "created_at": datetime.datetime.now().isoformat(),
                            "profile_username": profile_username,
                            "profile_full_name": profile_full_name,
                            "has_pdf": pdf_file.exists(),
                            "has_html": html_file.exists()
                        }
                        books.append(new_book)
                        save_user_books_local(user_id, books)
                        print(f"📚 Книга автоматически сохранена в библиотеку пользователя {user_id}")
                    else:
                        print("❌ Ошибка автоматического сохранения книги в библиотеку")
                else:
                    print("📚 Книга уже была сохранена в библиотеке пользователя")
            except Exception as save_error:
                print(f"❌ Ошибка автоматического сохранения: {save_error}")
        final_messages = [
            f"Смех свершился! Юмористическая книга о @{username} готова к прочтению: {html_file}",
            f"Ваша персональная комедия создана! @{username}, вы теперь — звезда стендапа: {html_file}",
            f"Весёлая история @{username} завершена! Каждая страница полна позитива: {html_file}",
            f"Книга-юмор @{username} готова! В ней живёт дух хорошего настроения: {html_file}"
        ]
        print(random.choice(final_messages))
    except Exception as e:
        print(f"Ошибка при создании юмористической книги о @{username}: {e}")
        try:
            basic_html = f"""
            <html>
            <head>
                <title>Юмористическая книга</title>
                <style>
                    body {{ background: #fffde7; font-family: sans-serif; padding: 20px; }}
                    .error {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Юмористическая книга</h1>
                    <p>Извините, произошла ошибка при создании книги: {e}</p>
                    <p>Попробуйте еще раз позже</p>
                </div>
            </body>
            </html>
            """
            html_file = Path("data") / run_id / "book.html"
            html_file.write_text(basic_html, encoding="utf-8")
        except Exception as final_error:
            print(f"Критическая ошибка: {final_error}")

def create_classic_humor_book_html(content: dict, analysis: dict, images: list) -> str:
    """Создает HTML классической юмористической книги с 10 главами и эпилогом"""
    import random
    from pathlib import Path
    from app.services.llm_client import generate_memoir_chapter, strip_cliches

    full_name = analysis.get('full_name', analysis.get('username', 'герой комедии'))
    username = analysis.get('username', 'comedian')
    followers = analysis.get('followers', 0)
    posts_count = analysis.get('posts_count', 0)
    bio = analysis.get('bio', '')
    post_details = analysis.get('post_details', [])
    real_captions = [p.get('caption', '') for p in post_details[:5] if p.get('caption')]
    locations = [p.get('location', '') for p in post_details[:3] if p.get('location')]

    processed_images = []
    selected_photo_data = []
    detected_gender = "unknown"

    if images:
        total_images = len(images)
        if total_images >= 10:
            selected_indices = random.sample(range(total_images), 10)
            selected_indices.sort()
        elif total_images >= 5:
            selected_indices = list(range(total_images))
            while len(selected_indices) < 10:
                random_idx = random.randint(0, total_images - 1)
                selected_indices.append(random_idx)
        else:
            selected_indices = []
            for _ in range(10):
                random_idx = random.randint(0, total_images - 1)
                selected_indices.append(random_idx)

        for i, idx in enumerate(selected_indices):
            img_path = images[idx]
            if isinstance(img_path, Path) and img_path.exists():
                try:
                    from PIL import Image, ImageEnhance
                    from io import BytesIO
                    import base64

                    with Image.open(img_path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        max_size = (700, 500)
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(1.05)
                        enhancer = ImageEnhance.Color(img)
                        img = enhancer.enhance(1.1)
                        buffer = BytesIO()
                        img.save(buffer, format='JPEG', quality=90)
                        img_str = base64.b64encode(buffer.getvalue()).decode()

                        processed_images.append(f"data:image/jpeg;base64,{img_str}")

                        fallback_descriptions = [
                            "На этом фото ты выглядишь как победитель конкурса на самую смешную улыбку!",
                            "Взгляд, который может рассмешить даже будильник.",
                            "Настроение: пятница после обеда!",
                            "Герой комедии в обычной жизни.",
                            "Смех сквозь объектив.",
                            "Когда шутка удалась!",
                            "Позитив на максимум.",
                            "Секретное оружие — улыбка!",
                            "В кадре — генератор хорошего настроения.",
                            "Тот самый момент, когда все смеются!"
                        ]

                        selected_photo_data.append({
                            'index': idx + 1,
                            'analysis': fallback_descriptions[i % len(fallback_descriptions)],
                            'image': f"data:image/jpeg;base64,{img_str}"
                        })
                except Exception as e:
                    print(f"❌ Ошибка обработки изображения {img_path}: {e}")

    def get_safe_photo_analysis(index: int, fallback_text: str) -> str:
        if not selected_photo_data:
            return fallback_text
        safe_index = index % len(selected_photo_data)
        return selected_photo_data[safe_index]['analysis']

    context_data = {
        'full_name': full_name,
        'username': username
    }

    chapter_configs = [
        {'key': 'meeting', 'title': 'Пролог: Первая встреча', 'prompt': f"""Ты стендап-комик. Выходишь на сцену и начинаешь разгон про {full_name}. Начни дерзко: 'Знаете, есть такие люди, которые...' Добавь абсурдные сравнения, неожиданные панчи, обращайся к залу. Не упоминай, что это книга. Пиши как будто ты на сцене и рвёшь зал. Используй дерзкий стиль, неожиданные повороты, панчи на панчах. НИКОГДА не пиши романтично!"""},
        {'key': 'first_impression', 'title': 'Глава первая: Первое впечатление', 'prompt': f"""Пошути про первое знакомство с {full_name}. Дерзко, с панчами. Придумай абсурдные сравнения типа 'она выглядела как...', добавь неожиданные повороты, разгони тему как настоящий комик. Пиши как будто ты на сцене и рвёшь зал. Не бойся абсурда и дерзости. НИКОГДА не пиши романтично!"""},
        {'key': 'world_view', 'title': 'Глава вторая: Мир глазами комика', 'prompt': f"""Разгони тему: как {full_name} видит мир. Придумай абсурдные ситуации, неожиданные наблюдения. Например: 'Она думает, что дождь — это просто небо чихает'. Добавь панчи, обращайся к залу дерзко. Пиши как будто ты на сцене и рвёшь зал. НИКОГДА не пиши романтично!"""},
        {'key': 'memorable_moments', 'title': 'Глава третья: Самые смешные моменты', 'prompt': f"""Сделай roast на {full_name}. Расскажи о самых нелепых моментах дерзко, с панчами. Не бойся абсурда, добавь шутки про повседневность, придумай неожиданные сравнения. Пиши как будто ты делаешь roast-номер и рвёшь зал. НИКОГДА не пиши романтично!"""},
        {'key': 'energy', 'title': 'Глава четвертая: Энергия и харизма', 'prompt': f"""Пошути про харизму {full_name}. Придумай абсурдные сравнения: 'Её энергия как...', 'Она может...'. Используй гиперболу, мемы, неожиданные панчи. Пиши дерзко, как будто ты на сцене и рвёшь зал. НИКОГДА не пиши романтично!"""},
        {'key': 'beauty_style', 'title': 'Глава пятая: Стиль и мода', 'prompt': f"""Разгони тему: стиль и мода {full_name}. Пошути про гардероб, аксессуары, нелепые тренды дерзко. Придумай абсурдные ситуации типа 'Она носит... как будто...'. Добавь панчи, обращайся к залу. НИКОГДА не пиши романтично!"""},
        {'key': 'mystery', 'title': 'Глава шестая: Загадка личности', 'prompt': f"""Придумай шуточные тайны про {full_name}. Например: 'Почему она всегда опаздывает? Может, она секретный агент смеха?' Добавь абсурдные теории заговора, дерзкие панчи. НИКОГДА не пиши романтично!"""},
        {'key': 'influence_on_me', 'title': 'Глава седьмая: Влияние на друзей', 'prompt': f"""Пошути, как {full_name} влияет на друзей. Придумай абсурдные примеры: 'После общения с ней все начинают...'. Добавь неожиданные панчи, дерзкие наблюдения. НИКОГДА не пиши романтично!"""},
        {'key': 'observations', 'title': 'Глава восьмая: Наблюдения за жизнью', 'prompt': f"""Разгони тему: наблюдения за жизнью {full_name}. Придумай абсурдные ситуации, неожиданные советы в стиле 'лайфхак от комика'. Пиши как будто рассказываешь залу анекдоты и рвёшь их. НИКОГДА не пиши романтично!"""},
        {'key': 'funny_final', 'title': 'Глава девятая: Финальный аккорд', 'prompt': f"""Финальный аккорд: пошути, что если бы {full_name} был(а) супергероем, его/её сила — заставлять людей смеяться даже в пробке. Заверши монологом с дерзкими панчами. НИКОГДА не пиши романтично!"""},
        {'key': 'gratitude_wishes', 'title': 'Эпилог: Благодарность и пожелания', 'prompt': f"""Поблагодари зал дерзко, пошути напоследок, пожелай всем хорошего настроения. Не упоминай, что это книга — только сцена, только смех! Заверши как настоящий стендап-номер. НИКОГДА не пиши романтично!"""},
    ]

    chapters = {}
    for i, config in enumerate(chapter_configs):
        try:
            generated_content = generate_memoir_chapter("humor_chapter", {
                'prompt': config['prompt'],
                'style': 'standup_comedy'
            })
            if not generated_content or len(generated_content.strip()) < 100:
                chapters[config['key']] = f"{config['title']} о {full_name} — это всегда повод для улыбки!"
            else:
                clean_content = strip_cliches(generated_content)
                chapters[config['key']] = clean_content
        except Exception as e:
            print(f"❌ Ошибка генерации главы '{config['title']}': {e}")
            chapters[config['key']] = f"{config['title']} о {full_name} — это всегда повод для улыбки!"

    book_title = f"Весёлые истории о {full_name}"

    # Создаём HTML для глав (исправленный блок!)
    chapter_pages_html = ""
    for i, config in enumerate(chapter_configs):
        if i < len(selected_photo_data):
            photo = selected_photo_data[i]
            # Извлекаем данные фото в отдельные переменные
            photo_image = photo['image']
            photo_analysis = photo['analysis']
            truncated_analysis = photo_analysis[:80] + '...' if len(photo_analysis) > 80 else photo_analysis
            
            image_block = f"""
            <div class="chapter-image-container">
                <img src="{photo_image}" alt="Photo for Chapter {i+1}" class="chapter-image">
                <p class="chapter-image-caption">
                    {truncated_analysis}
                </p>
            </div>
            """
        else:
            image_block = ""

        # Подготавливаем fallback текст для главы
        fallback_text = f"<p>{config['title']} о {full_name} — это всегда повод для улыбки!</p>"

        chapter_html = f"""
        <div id="chapter-{config['key']}" class="book-page chapter-page">
            <h3 class="chapter-subtitle">{config['title']}</h3>
            <h2 class="chapter-main-title">{config['title']}</h2>
            {image_block}
            <div class="chapter-body">
                {chapters.get(config['key'], fallback_text)}
            </div>
        </div>
        """
        chapter_pages_html += chapter_html

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Open+Sans:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        /* твои стили — оставлены без изменений для краткости */
    </style>
</head>
<body>
<!-- Cover Page -->
<div class="book-page cover-page">
    <div class="cover-content">
        <h1 class="cover-title">{full_name.upper()}</h1>
        <p class="cover-subtitle">Весёлые истории</p>
        <div class="cover-separator"></div>
        <p class="cover-dedication">Юмористическая биография с улыбкой</p>
    </div>
</div>
<!-- Table of Contents -->
<div class="book-page toc-page">
    <h2 class="toc-title">Содержание</h2>
    <ul class="toc-list">
        {''.join([f'''
        <li class="toc-item">
            <a href="#chapter-{config['key']}" class="chapter-name">{config['title']}</a>
            <span class="leader"></span>
            <a href="#chapter-{config['key']}" class="page-ref"></a>
        </li>
        ''' for config in chapter_configs])}
    </ul>
</div>

{chapter_pages_html}

<!-- Final Page -->
<div class="book-page final-page">
    <div class="final-content">
         <p>Спасибо, что дочитали до конца! Не забывайте улыбаться и делиться хорошим настроением с окружающими. 😄</p>
    </div>
    <div class="final-ornament">
        ✦
    </div>
    <div class="final-signature">
        <p>Пусть твоя история вдохновляет других.</p>
    </div>
</div>
</body>
</html>
"""

    return html
