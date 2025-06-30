import json
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from app.services.llm_client import strip_cliches, analyze_photo_for_memoir, generate_memoir_chapter
from typing import List, Tuple
import random
import time
import re
import asyncio
from fpdf import FPDF

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy не установлен, некоторые эффекты будут недоступны")

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
    """Создание HTML книги (с выбором формата: classic или zine)"""
    try:
        # Загружаем данные профиля
        run_dir = Path("data") / run_id
        posts_json = run_dir / "posts.json"
        images_dir = run_dir / "images"
        
        if posts_json.exists():
            posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
        else:
            posts_data = []
        
        # Анализируем профиль СНАЧАЛА
        analysis = analyze_profile_data(posts_data)
        username = analysis.get("username", "...")
        
        # Ждем загрузки изображений и собираем их
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
        if book_format == "zine":
            # Мозаичный зин - короткий контент
            content = generate_zine_content(analysis, actual_images)
            html = create_zine_html(content, analysis, actual_images)
        else:
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
            out = Path("data") / run_id
            out.mkdir(parents=True, exist_ok=True)
            
            html_file = out / "book.html"
            html_file.write_text(basic_html, encoding="utf-8")
            
            print(f"Создана запасная версия книги: {out / 'book.html'}")
            
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
        
        # Лёгкое размытие
        img = img.filter(ImageFilter.GaussianBlur(1.2))
        
        # Цветовая коррекция в теплые тона
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
        
        # Создаем теплый overlay
        overlay = Image.new('RGBA', img.size, (255, 220, 210, 25))  # peach #ffdcd2
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        # Добавляем grain только если numpy доступен
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
        try:
            return img.convert('RGB') if img.mode != 'RGB' else img
        except:
            # Создаем простое изображение-заглушку
            placeholder = Image.new('RGB', (400, 300), (240, 240, 240))
            return placeholder

def create_collage_spread(img1: Image.Image, img2: Image.Image, caption: str) -> str:
    """Создает коллаж-разворот из двух фотографий"""
    try:
        # Проверяем валидность изображений
        if img1 is None or img2 is None:
            print("❌ Одно из изображений для коллажа отсутствует")
            return ""
            
        if img1.size[0] == 0 or img1.size[1] == 0 or img2.size[0] == 0 or img2.size[1] == 0:
            print("❌ Недопустимый размер изображений для коллажа")
            return ""
        
        # Создаем холст для коллажа
        canvas_width = 1200
        canvas_height = 800
        canvas = Image.new('RGB', (canvas_width, canvas_height), (255, 250, 245))
        
        # Подготавливаем изображения
        img1_size = (500, 350)
        img2_size = (500, 350)
        
        # Безопасное изменение размера
        try:
            img1 = img1.resize(img1_size, Image.Resampling.LANCZOS)
            img2 = img2.resize(img2_size, Image.Resampling.LANCZOS)
        except Exception as resize_error:
            print(f"❌ Ошибка при изменении размера: {resize_error}")
            return ""
        
        # Применяем dream-pastel эффект
        img1 = apply_dream_pastel_effect(img1)
        img2 = apply_dream_pastel_effect(img2)
        
        # Размещаем изображения с небольшим поворотом
        try:
            img1_rotated = img1.rotate(-2, expand=True, fillcolor=(255, 250, 245))
            img2_rotated = img2.rotate(3, expand=True, fillcolor=(255, 250, 245))
            
            # Позиционируем на холсте
            pos1 = (50, 150)
            pos2 = (650, 200)
            
            canvas.paste(img1_rotated, pos1)
            canvas.paste(img2_rotated, pos2)
        except Exception as rotation_error:
            print(f"❌ Ошибка при повороте изображений: {rotation_error}")
            # Размещаем без поворота
            canvas.paste(img1, (50, 150))
            canvas.paste(img2, (650, 200))
        
        # Добавляем подпись посередине
        try:
            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Текст с тенью
            text_x = canvas_width // 2
            text_y = canvas_height - 100
            
            # Обрезаем слишком длинный caption
            if len(caption) > 50:
                caption = caption[:47] + "..."
            
            # Тень
            draw.text((text_x + 2, text_y + 2), caption, font=font, fill=(0, 0, 0, 100), anchor="mm")
            # Основной текст
            draw.text((text_x, text_y), caption, font=font, fill=(80, 60, 40), anchor="mm")
        except Exception as text_error:
            print(f"❌ Ошибка при добавлении текста: {text_error}")
        
        # Конвертируем в base64
        buffer = BytesIO()
        canvas.save(buffer, format='JPEG', quality=92)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ Ошибка при создании коллажа: {e}")
        return ""

def generate_zine_content(analysis: dict, images: list[Path]) -> dict:
    """Генерирует короткий контент для мозаичного зина"""
    
    # Фиксированные данные
    username = analysis.get('username', 'Неизвестный')
    followers = analysis.get('followers', 0)
    bio = analysis.get('bio', '')
    
    # Реальные данные
    real_captions = analysis.get('captions', ['Без слов'])[:3]
    locations = analysis.get('locations', ['неизвестное место'])[:2]
    
    # Анализируем фотографии для карточек (максимум 15 фото)
    photo_cards = []
    valid_images = []
    context = f"Instagram профиль @{username}, {followers} подписчиков, био: {bio}"
    
    # Романтические сообщения о процессе анализа фото
    analysis_messages = [
        "Вглядываюсь в детали каждого кадра...",
        "Анализирую эмоции, запечатлённые в ваших глазах...",
        "Изучаю композицию как вы выбираете ракурсы...",
        "Рассматриваю игру света на вашем лице...",
        "Декодирую скрытые послания в ваших взглядах..."
    ]
    
    for i, img_path in enumerate(images[:15]):  # Ограничиваем до 15 фото для зина
        if img_path.exists():
            try:
                # Создаем карточки разных типов
                card_types = ["micro", "trigger", "sms"]
                card_type = card_types[i % 3]
                
                # Заменяем удаленную функцию на прямой вызов
                focus_mapping = {
                    "micro": "first_impression",
                    "trigger": "story_creation", 
                    "sms": "hidden_emotions"
                }
                focus = focus_mapping.get(card_type, "first_impression")
                card_content = analyze_photo_for_memoir(img_path, context, focus)
                
                photo_cards.append({
                    'type': card_type,
                    'content': card_content,
                    'path': img_path
                })
                valid_images.append(img_path)
                
                # Романтическое сообщение о каждой карточке
                if i < len(analysis_messages):
                    print(f"{analysis_messages[i]} Карточка {i+1}/15")
                else:
                    print(f"💕 Карточка {i+1}/15: {card_content[:30]}... — ещё одна грань вашей души")
                    
            except Exception as e:
                print(f"💔 Не смог проанализировать кадр {img_path}: {e}")
    
    # Если фото меньше 3, создаем минимальный зин
    if len(valid_images) < 3:
        print(f"💝 Работаю с {len(valid_images)} фотографиями — даже малого достаточно для красоты")
    
    print(f"✅ Проанализировал {len(valid_images)} граней вашей личности из {len(images)} доступных моментов")
    
    scene_data = {
        'username': username,
        'followers': followers,
        'bio': bio,
        'captions': real_captions,
        'locations': locations,
        'photo_cards': photo_cards
    }
    
    content = {}
    
    # Заменяем удаленные функции на прямые вызовы memoir функций
    scene_mapping = {
        "hook": "meeting",
        "conflict": "social_analysis",
        "turn": "between_lines",
        "climax": "story_creation",
        "epilogue": "farewell_portrait"
    }
    
    # Романтические сообщения о создании глав
    chapter_messages = [
        "📝 Пишу завязку — как наши души встретились в цифровом пространстве...",
        "💭 Создаю конфликт — внутренняя борьба восхищения и смущения...", 
        "🔄 Формирую поворот — момент, когда понял вашу особенность...",
        "🎭 Выстраиваю кульминацию — пик эмоционального напряжения...",
        "💫 Завершаю эпилогом — что останется в памяти навсегда..."
    ]
    
    try:
        # 1. ЗАВЯЗКА - дневниковая запись (максимум 3 предложения)
        print(chapter_messages[0])
        hook = generate_memoir_chapter(scene_mapping["hook"], scene_data)
        content['prologue'] = strip_cliches(hook)
        print(f"✅ Завязка готова: романтическое знакомство описано")
    except Exception as e:
        print(f"💔 Ошибка завязки: {e}")
        content['prologue'] = f"Наткнулся на @{username} случайно. Что-то зацепило."
    
    try:
        # 2. КОНФЛИКТ - SMS-стиль (максимум 4 строки)
        print(chapter_messages[1])
        conflict = generate_memoir_chapter(scene_mapping["conflict"], scene_data)
        content['emotions'] = strip_cliches(conflict)
        print(f"✅ Конфликт создан: внутренние противоречия показаны")
    except Exception as e:
        print(f"💔 Ошибка конфликта: {e}")
        content['emotions'] = f"— {real_captions[0] if real_captions else 'Все хорошо'}\n— Но глаза говорят другое."
    
    try:
        # 3. ПОВОРОТ - момент озарения (максимум 3 предложения)
        print(chapter_messages[2])
        turn = generate_memoir_chapter(scene_mapping["turn"], scene_data)
        content['places'] = strip_cliches(turn)
        print(f"✅ Поворот написан: ключевой момент понимания найден")
    except Exception as e:
        print(f"💔 Ошибка поворота: {e}")
        content['places'] = f"Один кадр из {locations[0] if locations else 'неизвестного места'} изменил все. Здесь пахло честностью."
    
    try:
        # 4. КУЛЬМИНАЦИЯ - цитаты комментариев
        print(chapter_messages[3])
        climax = generate_memoir_chapter(scene_mapping["climax"], scene_data)
        content['community'] = strip_cliches(climax)
        print(f"✅ Кульминация достигнута: пик эмоций передан словами")
    except Exception as e:
        print(f"💔 Ошибка кульминации: {e}")
        content['community'] = f"{followers} человек отреагировали:\n— Наконец-то ты показал себя настоящего\n— Спасибо за честность"
    
    try:
        # 5. ЭПИЛОГ - приглашение (максимум 2 предложения)
        print(chapter_messages[4])
        epilogue = generate_memoir_chapter(scene_mapping["epilogue"], scene_data)
        content['legacy'] = strip_cliches(epilogue)
        print(f"✅ Эпилог завершён: прощальные слова произнесены с нежностью")
    except Exception as e:
        print(f"💔 Ошибка эпилога: {e}")
        content['legacy'] = "Листаю ленту в поиске нового дикого цветка. А вдруг это будешь ты?"
    
    # Метаданные
    content['title'] = f"Зин @{username}"
    content['photo_cards'] = photo_cards
    content['valid_images_count'] = len(valid_images)
    content['reading_time'] = "5 минут"
    
    return content

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
    
    # Обрабатываем изображения (умный выбор - не подряд, а разнообразно)
    processed_images = []
    detected_gender = "unknown"
    selected_photo_data = []  # Данные о выбранных фото для анализа
    
    if images:
        # Еще более умная логика выбора фотографий - не подряд!
        selected_indices = []
        total_images = len(images)
        
        if total_images >= 10:
            # Если много фото - берем разнообразно: 1, 5, 11, 32, последнее
            selected_indices = [
                0,  # первое
                min(4, total_images - 1),  # 5-е или близкое
                min(10, total_images - 1),  # 11-е или близкое  
                min(total_images // 3, total_images - 1),  # треть
                min(total_images * 2 // 3, total_images - 1),  # две трети
                total_images - 1  # последнее
            ]
        elif total_images >= 6:
            # Средне количество - берем 1, 3, 5, последнее
            selected_indices = [
                0,  # первое
                min(2, total_images - 1),  # 3-е
                min(4, total_images - 1),  # 5-е
                total_images - 1  # последнее
            ]
        elif total_images >= 3:
            # Мало фото - берем 1-е, среднее, последнее
            selected_indices = [0, total_images // 2, total_images - 1]
        else:
            # Совсем мало - берем что есть
            selected_indices = list(range(total_images))
        
        # Убираем дубликаты и сортируем
        selected_indices = sorted(list(set(selected_indices)))
        print(f"📸 Умный выбор фото: из {total_images} беру позиции {selected_indices}")
        
        # Анализируем первое фото для определения пола
        if images and images[0].exists():
            print("🔍 Анализирую фото для определения пола...")
            detected_gender = analyze_photo_for_gender(images[0])
            print(f"✅ Определен пол: {detected_gender}")
        
        # Обрабатываем выбранные фотографии
        for i, idx in enumerate(selected_indices[:6]):  # Максимум 6 фото
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
                        
                        # БЫСТРЫЙ FALLBACK вместо медленного анализа фото
                        quick_photo_analysis = [
                            "Взгляд полон жизни и искренности",
                            "Естественная красота без фильтров", 
                            "Особая атмосфера в каждом кадре",
                            "Эмоции, которые говорят сами за себя",
                            "Харизма и энергетика через экран",
                            "Стиль и грация в каждом движении"
                        ][i % 6]
                        
                        selected_photo_data.append({
                            'index': idx + 1,  # Номер фото в профиле
                            'analysis': quick_photo_analysis,  # Быстрый fallback
                            'image': f"data:image/jpeg;base64,{img_str}"
                        })
                        
                        print(f"✅ Обработано фото #{idx+1} из профиля")
                except Exception as e:
                    print(f"❌ Ошибка обработки изображения {img_path}: {e}")
    
    # Подготавливаем контекст для ИИ с анализом фото
    context_data = {
        'username': username,
        'full_name': full_name,
        'followers': followers,
        'posts_count': posts_count,
        'bio': bio,
        'captions': real_captions[:5],  # Первые 5 подписей
        'locations': locations[:3],     # Первые 3 локации
        'video_content': video_content[:3],  # Первые 3 видео
        'has_videos': len(video_content) > 0,
        'selected_photos': selected_photo_data  # Данные о выбранных фото
    }
    
    # Создаем 10 подробных глав с помощью ИИ
    chapters = {}
    
    # Используем результат анализа фото для определения пола
    def get_gender_from_analysis(detected_gender: str, name: str) -> str:
        if detected_gender == "female":
            return "female"
        elif detected_gender == "male":
            return "male"
        else:
            # Fallback к анализу имени
            female_names = ['арина', 'анна', 'елена', 'мария', 'ольга', 'татьяна', 'наталья', 'светлана', 'ирина', 'екатерина', 'юлия', 'алина', 'дарья', 'алиса', 'софия', 'анастасия', 'валерия', 'виктория', 'диана', 'карина', 'кристина', 'маргарита', 'милана', 'полина', 'ульяна', 'aruzhan', 'aida', 'amina', 'diana', 'emma', 'kate', 'maria', 'anna', 'elena', 'sofia', 'alina', 'daria', 'julia', 'kristina', 'milana', 'polina', 'valeria', 'victoria']
            name_lower = name.lower()
            for fem_name in female_names:
                if fem_name in name_lower:
                    return 'female'
            return 'male'
    
    gender = get_gender_from_analysis(detected_gender, full_name)
    gender_word = 'красивая' if gender == 'female' else 'красивый'
    she_he = 'она' if gender == 'female' else 'он'
    her_his = 'её' if gender == 'female' else 'его'
    love_word = 'влюблен в неё' if gender == 'female' else 'влюблен в него'
    
    print(f"👤 Итоговое определение: {gender} ({'девушка' if gender == 'female' else 'парень'})")
    
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
            'title': 'История знакомства',
            'emotional_intro': 'Дорогой {username}, я долго думал, что подарить тебе...',
            'prompt': f"""Напиши главу "История знакомства" с {full_name} от первого лица (5-6 абзацев).
            
            ПОЛ: {gender} ({'девушка' if gender == 'female' else 'парень'}) - используй "{she_he}", "{her_his}"
            
            НАЧНИ эмоционально и лично: "Дорогой {full_name}, я долго думал, что подарить тебе..."
            
            АНАЛИЗ ПЕРВОГО ФОТО:
            {selected_photo_data[0]['analysis'] if selected_photo_data else 'Фото сразу зацепило взгляд'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Личное обращение и размышления о подарке
            2. Абзац: Как все началось - листал Instagram, увидел твой профиль
            3. Абзац: Первое впечатление от профиля и фотографий
            4. Абзац: Что заставило остановиться и изучать дальше
            5. Абзац: Твоя особенность - умение находить красоту
            6. Абзац: Что ты значишь для меня, даже не зная об этом
            
            СТИЛЬ:
            - Очень личный, интимный тон
            - Прямые обращения: "тебе", "твой", "ты"
            - Подробные описания чувств и эмоций
            - Романтичные метафоры: "особое сияние", "магнетизм"
            - Философские размышления о красоте
            - Теплые, искренние признания
            
            РЕАЛЬНЫЕ ДАННЫЕ:
            - Имя: {full_name}
            - Username: @{username}  
            - Подписчики: {followers}
            - Реальная подпись: "{real_captions[0] if real_captions else 'твоя загадочная подпись'}"
            
            БЕЗ хэштегов и технических терминов. Пиши как романтичное письмо от влюбленного человека."""
        },
        {
            'key': 'first_impression', 
            'title': 'Первые впечатления',
            'emotional_intro': 'Знаешь, что меня поразило в первые минуты знакомства с твоим профилем?',
            'prompt': f"""Напиши главу "Первые впечатления" от {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с восхищения: "Знаешь, что меня поразило в первые минуты знакомства с твоим профилем?"
            
            АНАЛИЗ ВТОРОГО ФОТО:
            {selected_photo_data[1]['analysis'] if len(selected_photo_data) > 1 else 'Каждое фото рассказывает историю'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Что поразило с первого взгляда - искренность
            2. Абзац: Анализ фотографий - особая атмосфера в каждом кадре
            3. Абзац: Подписи к фото и их глубина
            4. Абзац: Изучение профиля в деталях - каждый кадр рассказывает историю
            5. Абзац: Подробное описание внешности - черты лица, глаза, улыбка
            6. Абзац: Заключение о честности и открытости
            
            ДЕТАЛЬНЫЕ ОПИСАНИЯ:
            - Черты лица: "прекрасные черты лица - правильные, гармоничные"
            - Глаза: "особенно выразительны - в них читается ум, доброта и глубина души"
            - Улыбка: "освещает всё вокруг, не наигранная, а настоящая"
            - Общее впечатление: многогранная красота
            
            КОНКРЕТНАЯ ПОДПИСЬ: "{real_captions[0] if real_captions else 'твоя особенная подпись'}"
            
            Пиши как подробный портрет любимого человека."""  
        },
        {
            'key': 'world_view',
            'title': 'Твой взгляд на мир',
            'emotional_intro': 'Больше всего меня поражает то, как ты видишь мир вокруг себя...',
            'prompt': f"""Напиши главу "Твой взгляд на мир" о {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ размышлением: "Больше всего меня поражает то, как ты видишь мир вокруг себя..."
            
            АНАЛИЗ ТРЕТЬЕГО ФОТО:
            {selected_photo_data[2]['analysis'] if len(selected_photo_data) > 2 else 'Душа, видная в творчестве'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Способность находить прекрасное в обыденном
            2. Абзац: Анализ композиции и выбора моментов
            3. Абзац: Движение и естественность в кадрах
            4. Абзац: Подписи как окно в душу
            5. Абзац: Внешность как отражение внутреннего мира - описание
            6. Абзац: Дар видеть красоту - редкое качество
            
            ДЕТАЛЬНЫЕ ОПИСАНИЯ ВНЕШНОСТИ:
            - "Твоя внешность отражает твой внутренний мир"
            - "Ты красив той естественной красотой, которая не нуждается в прикрасах"
            - "Твое лицо открытое, честное, в нем нет ни тени лжи"
            - "Твои черты благородны - высокий лоб говорит об уме, выразительные глаза - о чувствительности"
            - "У тебя прекрасная осанка - ты держишься с достоинством"
            
            БИО: "{bio if bio else 'Твое молчание говорит больше любых слов'}"
            
            Пиши как глубокий психологический портрет."""
        },
        {
            'key': 'memorable_moments',
            'title': 'Моменты, которые запомнились',
            'emotional_intro': 'Есть кадры, которые врезаются в память навсегда...',
            'prompt': f"""Напиши главу "Моменты, которые запомнились" о {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с признания: "Есть кадры, которые врезаются в память навсегда..."
            
            АНАЛИЗ ЧЕТВЕРТОГО ФОТО:
            {selected_photo_data[3]['analysis'] if len(selected_photo_data) > 3 else 'Особые моменты в кадре'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Особые кадры, которые запомнились навсегда
            2. Абзац: Конкретная фотография - описание и впечатления
            3. Абзац: Подпись "{real_captions[0] if real_captions else '🤠'}" - как она открыла часть души
            4. Абзац: Честность эмоций - не боишься показывать настоящие чувства
            5. Абзац: Живая красота - описание глаз и их выразительности
            6. Абзац: Искренность как главное качество
            
            ДЕТАЛЬНЫЕ ОПИСАНИЯ:
            - "Твоя красота не статична - она живая, меняющаяся"
            - "Твои глаза - это отдельная поэма. Они глубокие, выразительные"
            - "Когда ты радуешься, они сияют особым светом"
            - "Когда задумываешься - становятся глубокими озерами мудрости"
            - "В каждом движении, в каждом взгляде чувствуется личность"
            - "Твоя улыбка - это твоя визитная карточка"
            
            Пиши как дневник наблюдений влюбленного человека."""
        },
        {
            'key': 'energy',
            'title': 'Твоя энергетика',
            'emotional_intro': 'В тебе есть особая энергетика, которая чувствуется даже через экран телефона...',
            'prompt': f"""Напиши главу "Твоя энергетика" о {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с наблюдения: "В тебе есть особая энергетика, которая чувствуется даже через экран телефона..."
            
            АНАЛИЗ ПЯТОГО ФОТО:
            {selected_photo_data[4]['analysis'] if len(selected_photo_data) > 4 else 'Энергия, видная в каждом кадре'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Особая энергетика, которая чувствуется через экран
            2. Абзац: Умение быть собой в любой ситуации
            3. Абзац: Естественность и способность давать энергию людям
            4. Абзац: Аура доброты и позитива
            5. Абзац: Подробные описания внешности - кожа, волосы, руки
            6. Абзац: Уникальность в мире похожих людей
            
            ДЕТАЛЬНЫЕ ОПИСАНИЯ ВНЕШНОСТИ:
            - "У тебя красивая кожа - здоровая, сияющая, она буквально светится изнутри"
            - "Твои волосы красивые, ухоженные, они обрамляют твое лицо как картину в раме"
            - "Твои руки красивые и выразительные"
            - "Даже простой жест у тебя получается грациозным и естественным"
            - "В твоих движениях есть особая пластика - ты двигаешься как танцор"
            
            Пиши как восхищенный портрет харизматичного человека."""
        },
        {
            'key': 'beauty_style',
            'title': 'О красоте и стиле',
            'emotional_intro': 'Красота - понятие субъективное, но в твоем случае она очевидна для всех...',
            'prompt': f"""Напиши главу "О красоте и стиле" о {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с утверждения: "Красота - понятие субъективное, но в твоем случае она очевидна для всех..."
            
            АНАЛИЗ ШЕСТОГО ФОТО:
            {selected_photo_data[5]['analysis'] if len(selected_photo_data) > 5 else 'Красота и стиль в каждом движении'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Гармония внутреннего и внешнего
            2. Абзац: Врожденное чувство стиля и естественность
            3. Абзац: Собственная эстетика, не следование трендам
            4. Абзац: Подробное описание лица как произведения искусства
            5. Абзац: Детали красоты - брови, ресницы, кожа, улыбка
            6. Абзац: Красота души через внешние проявления
            
            ДЕТАЛЬНЫЕ ОПИСАНИЯ КРАСОТЫ:
            - "Твое лицо - это произведение искусства. Правильные пропорции, выразительные черты"
            - "Твой нос изящный и аристократичный. Твои скулы красиво очерчены"
            - "У тебя красивые брови - четкие, выразительные, они идеально обрамляют твои глаза"
            - "Твои ресницы длинные и густые, они создают красивую тень на щеках"
            - "Твоя кожа безупречна - гладкая, здоровая, с естественным сиянием"
            - "Когда ты улыбаешься, твои глаза прищуриваются от радости, на щеках появляются милые ямочки"
            
            Пиши как поэтическое описание идеальной красоты."""
        },
        {
            'key': 'mystery',
            'title': 'Твоя загадочность',
            'emotional_intro': 'В тебе есть особая загадочность, которая не дает покоя...',
            'prompt': f"""Напиши главу "Твоя загадочность" о {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с интриги: "В тебе есть особая загадочность, которая не дает покоя..."
            
            АНАЛИЗ СЕДЬМОГО ФОТО:
            {selected_photo_data[6]['analysis'] if len(selected_photo_data) > 6 else selected_photo_data[0]['analysis'] if selected_photo_data else 'Загадочность в каждом взгляде'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Особая загадочность - не эффект, а глубина личности
            2. Абзац: Каждый кадр открывает что-то новое
            3. Абзац: Интерес к твоим мыслям в моменты задумчивости
            4. Абзац: Загадочность взгляда и предположения о голосе
            5. Абзац: Описание походки и манеры держаться
            6. Абзац: Естественная загадочность многогранной личности
            
            ПРЕДПОЛОЖЕНИЯ И ОПИСАНИЯ:
            - "Твой взгляд особенно загадочен. В нем есть глубина океана"
            - "У тебя красивый голос - даже если я его не слышал, я чувствую его по твоему лицу"
            - "Должно быть, он мелодичный, теплый, с особыми интонациями"
            - "Твоя походка, должно быть, грациозная и уверенная"
            - "Ты двигаешься как человек, который знает, чего хочет от жизни"
            - "В твоих жестах есть элегантность, в твоей манере держаться - достоинство"
            
            Пиши как попытку разгадать прекрасную тайну."""
        },
        {
            'key': 'influence_on_me',
            'title': 'Влияние на меня',
            'emotional_intro': 'Знаешь, что странно? Ты изменил мой взгляд на многие вещи...',
            'prompt': f"""Напиши главу "Влияние на меня" о {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с удивления: "Знаешь, что странно? Ты изменил мой взгляд на многие вещи..."
            
            АНАЛИЗ ВОСЬМОГО ФОТО:
            {selected_photo_data[7]['analysis'] if len(selected_photo_data) > 7 else selected_photo_data[1]['analysis'] if len(selected_photo_data) > 1 else 'Влияние, что изменило многое'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Удивление тому, как ты изменил автора
            2. Абзац: Новое внимание к деталям вокруг
            3. Абзац: Конкретная подпись "{real_captions[0] if real_captions else '🤠...'}" и ее влияние
            4. Абзац: Изменение восприятия красоты и обычных вещей
            5. Абзац: Уроки о настоящей привлекательности и искренности
            6. Абзац: Вдохновение быть естественным и открытым
            
            КОНКРЕТНЫЕ ИЗМЕНЕНИЯ:
            - "Стал больше внимания обращать на детали вокруг себя"
            - "Игру света в окне кафе, выражение лиц прохожих"
            - "Теперь, проходя по улице, я ловлю себя на мысли: 'А как бы это увидел {full_name}?'"
            - "Ты показал мне, что красота не требует дорогих декораций"
            - "Благодаря тебе я понял, что настоящая привлекательность - это не только внешность"
            
            Пиши как честное признание о том, как человек изменил твою жизнь."""
        },
        {
            'key': 'observations',
            'title': 'Мои наблюдения',
            'emotional_intro': 'За время наблюдения за тобой я сделал несколько интересных открытий...',
            'prompt': f"""Напиши главу "Мои наблюдения" о {full_name} (5-6 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с открытия: "За время наблюдения за тобой я сделал несколько интересных открытий..."
            
            АНАЛИЗ ДЕВЯТОГО ФОТО:
            {selected_photo_data[8]['analysis'] if len(selected_photo_data) > 8 else selected_photo_data[2]['analysis'] if len(selected_photo_data) > 2 else 'Наблюдения за особенностями'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Внимательность к деталям и глаз художника
            2. Абзац: Умение быть в моменте, отсутствие наигранности
            3. Абзац: Предпочтение качества количеству в постах
            4. Абзац: Способность находить красоту в простоте
            5. Абзац: Подробные наблюдения о внешности - фотогеничность, руки, стиль
            6. Абзац: Любовь к свету и умение его использовать, осанка
            
            ДЕТАЛЬНЫЕ НАБЛЮДЕНИЯ:
            - "Твое лицо очень фотогеничное. У тебя нет 'плохих' ракурсов"
            - "У тебя очень выразительные руки. Даже когда они просто лежат в кадре, они рассказывают историю"
            - "Твои пальцы длинные и изящные, твои жесты грациозные"
            - "Ты не гонишься за брендами, но всегда выглядишь стильно и уместно"
            - "Ты любишь свет. На многих твоих фото видно, как ты умело используешь естественное освещение"
            - "Твоя осанка говорит о внутренней уверенности"
            
            Пиши как внимательные заметки восхищенного наблюдателя."""
        },
        {
            'key': 'gratitude_wishes',
            'title': 'Пожелания и благодарность',
            'emotional_intro': '{username}, эта книга подходит к концу, но мои мысли о тебе на этом не заканчиваются...',
            'prompt': f"""Напиши главу "Пожелания и благодарность" для {full_name} (6-7 абзацев).
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ с личного обращения: "{full_name}, эта книга подходит к концу, но мои мысли о тебе на этом не заканчиваются..."
            
            АНАЛИЗ ФИНАЛЬНОГО ФОТО:
            {selected_photo_data[9]['analysis'] if len(selected_photo_data) > 9 else selected_photo_data[0]['analysis'] if selected_photo_data else 'Образ, что останется в памяти навсегда'}
            
            СТРУКТУРА ГЛАВЫ:
            1. Абзац: Личное обращение и упоминание био "{bio if bio else 'твоя особенная натура'}"
            2. Абзац: Понимание счастья через наблюдение за тобой
            3. Абзац: Пожелания продолжать быть собой
            4. Абзац: Пожелания найти важное в жизни
            5. Абзац: Пожелания красоты, любви и успеха
            6. Абзац: Благодарность за то, что ты есть
            7. Абзац: Финальные слова поддержки и подпись
            
            РАЗВЕРНУТЫЕ ПОЖЕЛАНИЯ:
            - "Продолжай быть собой. Продолжай фотографировать мир таким, каким ты его видишь"
            - "Пусть твоя красота только расцветает с годами"
            - "Я желаю тебе встретить людей, которые будут ценить тебя таким, какой ты есть"
            - "Пусть твоя жизнь будет полна ярких моментов, достойных того, чтобы их запечатлеть"
            - "Желаю тебе никогда не потерять эту детскую способность удивляться миру"
            - "Я желаю тебе любви - настоящей, глубокой, взаимной"
            
            ФИНАЛЬНЫЕ СЛОВА:
            - "Спасибо тебе за то, что ты есть"
            - "Этот мир стал лучше с тобой в нем"
            - "Помни - ты важен, ты ценен, ты любим"
            - "С глубокой благодарностью и восхищением, твой тайный поклонник"
            
            Пиши как искреннее финальное письмо с пожеланиями всего самого лучшего."""
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
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400;1,600&family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
    :root {{
        --paper: #fefcf8;
        --ink: #2c2a26;
        --soft-ink: #5a5652;
        --accent: #8b4513;
        --gold: #d4af8c;
        --shadow: rgba(60, 50, 40, 0.15);
        --warm-cream: #f9f7f4;
    }}
    
    body {{
        font-family: 'Times New Roman', 'Georgia', serif;
        background: var(--paper);
        color: var(--ink);
        line-height: 1.6;
        font-size: 16px;
        margin: 0;
        padding: 0;
        max-width: 800px;
        margin: 0 auto;
    }}
    
    .memoir-page {{
        min-height: 95vh;
        padding: 2.5cm 2.5cm 3cm 2.5cm;
        background: white;
        box-shadow: 0 8px 40px var(--shadow);
        margin: 15px auto;
        page-break-after: always;
        position: relative;
        border-left: 3px solid var(--gold);
    }}
    
    .memoir-page:last-child {{
        page-break-after: auto;
    }}
    
    /* Обложка как личный подарок */
    .cover-memoir {{
        text-align: center;
        padding: 4cm 2cm;
        background: linear-gradient(135deg, var(--paper) 0%, var(--warm-cream) 100%);
        border: 2px solid var(--gold);
        border-left: 6px solid var(--accent);
    }}
    
    .cover-title, .cover-subtitle, .cover-epigraph, .memoir-author {{
        max-width: none;
        width: 100%;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    .cover-title {{
        font-family: 'Times New Roman', serif;
        font-size: 2.8rem;
        font-weight: bold;
        color: var(--ink);
        margin-bottom: 1.5rem;
        letter-spacing: 1px;
        line-height: 1.3;
    }}
    
    .cover-subtitle {{
        font-family: 'Times New Roman', serif;
        font-style: italic;
        font-size: 1.2rem;
        color: var(--soft-ink);
        margin-bottom: 2.5rem;
    }}
    
    .cover-epigraph {{
        font-style: italic;
        color: var(--soft-ink);
        border-top: 1px solid var(--gold);
        border-bottom: 1px solid var(--gold);
        padding: 2rem 1rem;
        max-width: 450px;
        margin: 0 auto 2.5rem auto;
        position: relative;
        font-size: 1.1rem;
        line-height: 1.5;
    }}
    
    .memoir-author {{
        font-size: 1.1rem;
        color: var(--soft-ink);
        margin-top: 2rem;
        line-height: 1.4;
    }}
    
    /* Заголовки глав */
    .chapter-header {{
        margin-bottom: 2.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--gold);
    }}
    
    .chapter-number {{
        font-family: 'Times New Roman', serif;
        font-size: 0.9rem;
        color: var(--soft-ink);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.8rem;
    }}
    
    .chapter-title {{
        font-family: 'Times New Roman', serif;
        font-size: 2rem;
        font-weight: bold;
        color: var(--accent);
        margin: 0;
        font-style: italic;
    }}
    
    /* Параграфы как в настоящей книге */
    .memoir-text {{
        white-space: pre-line;
        text-align: justify;
        line-height: 1.7;
        font-size: 16px;
        letter-spacing: 0.2px;
        text-indent: 1.5em;
        margin-bottom: 1.2em;
        hyphens: auto;
        word-spacing: 0.1em;
    }}
    
    .memoir-text p {{
        margin-bottom: 1.2em;
        text-indent: 1.5em;
    }}
    
    .memoir-text p:first-child {{
        text-indent: 0;
    }}
    
    /* Изображения как в книге */
    .memoir-photo {{
        margin: 2.5rem 0;
        text-align: center;
        page-break-inside: avoid;
    }}
    
    .photo-frame {{
        display: inline-block;
        padding: 15px;
        background: var(--warm-cream);
        border-radius: 8px;
        box-shadow: 0 4px 20px var(--shadow);
        border: 1px solid var(--gold);
    }}
    
    .photo-frame img {{
        max-width: 100%;
        max-height: 300px;
        border-radius: 4px;
        border: 1px solid #ddd;
    }}
    
    .photo-caption {{
        font-family: 'Times New Roman', serif;
        font-style: italic;
        font-size: 0.9rem;
        color: var(--soft-ink);
        margin-top: 1rem;
        text-align: center;
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.4;
    }}
    
    /* Финальная страница */
    .memoir-finale {{
        text-align: center;
        margin-top: 3rem;
        padding: 2.5rem 2rem;
        background: var(--warm-cream);
        border-radius: 8px;
        border: 1px solid var(--gold);
    }}
    
    .memoir-signature {{
        font-family: 'Times New Roman', serif;
        font-style: italic;
        font-size: 1.2rem;
        color: var(--accent);
        margin-top: 1.5rem;
        line-height: 1.4;
    }}
    
    /* Метаданные */
    .memoir-meta {{
        margin-top: 2.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--gold);
        font-size: 0.85rem;
        color: var(--soft-ink);
        text-align: center;
        line-height: 1.5;
    }}
    
    /* Оглавление */
    .table-of-contents {{
        margin: 2.5rem 0;
        padding: 2rem;
        background: var(--warm-cream);
        border-radius: 8px;
        border: 1px solid var(--gold);
    }}
    
    .toc-title {{
        font-family: 'Times New Roman', serif;
        font-size: 1.6rem;
        color: var(--accent);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }}
    
    .toc-item {{
        margin-bottom: 0.8rem;
        padding: 0.4rem 0;
        border-bottom: 1px dotted var(--gold);
        display: flex;
        justify-content: space-between;
        font-size: 0.95rem;
    }}
    
    .toc-chapter {{
        font-weight: 500;
        color: var(--ink);
    }}
    
    .toc-page {{
        color: var(--soft-ink);
        font-style: italic;
    }}
    
    @media (max-width: 768px) {{
        .memoir-page {{
            padding: 2cm 1.5cm;
            margin: 10px;
        }}
        
        .cover-title {{
            font-size: 2.2rem;
        }}
        
        .chapter-title {{
            font-size: 1.6rem;
        }}
        
        .memoir-text {{
            font-size: 15px;
        }}
    }}
    
    @media print {{
        body {{
            background: white;
            margin: 0;
        }}
        
        .memoir-page {{
            box-shadow: none;
            margin: 0;
            border: none;
        }}
        
        .photo-frame {{
            transform: none;
        }}
    }}
    </style>
</head>
<body>

<!-- ОБЛОЖКА ПОДАРКА -->
<div class="memoir-page cover-memoir">
    <h1 class="cover-title">{book_title}</h1>
    <p class="cover-subtitle">Персональная книга в подарок</p>
    
    <div class="cover-epigraph">
        Дорогой {full_name},<br>
        эта книга написана специально для тебя<br>
        с большой любовью и восхищением
    </div>
    
    <div class="memoir-author">
        <strong>Для:</strong> {full_name}<br>
        <small>@{username}</small><br>
        <small>С особой теплотой</small>
    </div>
</div>
    
<!-- ОГЛАВЛЕНИЕ -->
<div class="memoir-page">
    <div class="table-of-contents">
        <h2 class="toc-title">Что внутри этой книги</h2>
        
        <div class="toc-item">
            <span class="toc-chapter">История знакомства</span>
            <span class="toc-page">3</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Первые впечатления</span>
            <span class="toc-page">4</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Твой взгляд на мир</span>
            <span class="toc-page">5</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Моменты, которые запомнились</span>
            <span class="toc-page">6</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Твоя энергетика</span>
            <span class="toc-page">7</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">О красоте и стиле</span>
            <span class="toc-page">8</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Твоя загадочность</span>
            <span class="toc-page">9</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Влияние на меня</span>
            <span class="toc-page">10</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Мои наблюдения</span>
            <span class="toc-page">11</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Пожелания и благодарность</span>
            <span class="toc-page">12</span>
        </div>
    </div>
</div>

<!-- ГЛАВА 1: ИСТОРИЯ ЗНАКОМСТВА -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава первая</div>
        <h2 class="chapter-title">История знакомства</h2>
    </div>
    
    <div class="memoir-text">{chapters['meeting']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Твоя красота"></div><div class="photo-caption">В этом взгляде - целая вселенная</div></div>' if processed_images else ''}
</div>

<!-- ГЛАВА 2: ПЕРВЫЕ ВПЕЧАТЛЕНИЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава вторая</div>
        <h2 class="chapter-title">Первые впечатления</h2>
    </div>
    
    <div class="memoir-text">{chapters['first_impression']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Твоя особенность"></div><div class="photo-caption">Красота, которая не нуждается в словах</div></div>' if len(processed_images) > 1 else ''}
</div>

<!-- ГЛАВА 3: ТВОЙ ВЗГЛЯД НА МИР -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава третья</div>
        <h2 class="chapter-title">Твой взгляд на мир</h2>
    </div>
    
    <div class="memoir-text">{chapters['world_view']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[2]}" alt="Как ты видишь мир"></div><div class="photo-caption">Сияние души, которое видно даже через экран</div></div>' if len(processed_images) > 2 else ''}
</div>

<!-- ГЛАВА 4: МОМЕНТЫ, КОТОРЫЕ ЗАПОМНИЛИСЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава четвертая</div>
        <h2 class="chapter-title">Моменты, которые запомнились</h2>
    </div>
    
    <div class="memoir-text">{chapters['memorable_moments']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[3]}" alt="Запомнившиеся моменты"></div><div class="photo-caption">Мгновение, которое хочется растянуть на вечность</div></div>' if len(processed_images) > 3 else ''}
</div>

<!-- ГЛАВА 5: ТВОЯ ЭНЕРГЕТИКА -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава пятая</div>
        <h2 class="chapter-title">Твоя энергетика</h2>
    </div>
    
    <div class="memoir-text">{chapters['energy']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[4]}" alt="Твоя энергетика"></div><div class="photo-caption">Энергия света, что делает мир ярче</div></div>' if len(processed_images) > 4 else ''}
</div>

<!-- ГЛАВА 6: О КРАСОТЕ И СТИЛЕ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава шестая</div>
        <h2 class="chapter-title">О красоте и стиле</h2>
    </div>
    
    <div class="memoir-text">{chapters['beauty_style']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[5]}" alt="Твоя красота и стиль"></div><div class="photo-caption">Гармония, созданная самой природой</div></div>' if len(processed_images) > 5 else ''}
</div>

<!-- ГЛАВА 7: ТВОЯ ЗАГАДОЧНОСТЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава седьмая</div>
        <h2 class="chapter-title">Твоя загадочность</h2>
    </div>
    
    <div class="memoir-text">{chapters['mystery']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[6]}" alt="Твоя загадочность"></div><div class="photo-caption">Глубина, в которой хочется утонуть</div></div>' if len(processed_images) > 6 else ''}
</div>

<!-- ГЛАВА 8: ВЛИЯНИЕ НА МЕНЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава восьмая</div>
        <h2 class="chapter-title">Влияние на меня</h2>
    </div>
    
    <div class="memoir-text">{chapters['influence_on_me']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[7]}" alt="Твое влияние"></div><div class="photo-caption">Образ, что изменил мое восприятие мира</div></div>' if len(processed_images) > 7 else ''}
</div>

<!-- ГЛАВА 9: МОИ НАБЛЮДЕНИЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава девятая</div>
        <h2 class="chapter-title">Мои наблюдения</h2>
    </div>
    
    <div class="memoir-text">{chapters['observations']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[8]}" alt="Мои наблюдения"></div><div class="photo-caption">Совершенство в каждой детали</div></div>' if len(processed_images) > 8 else ''}
</div>

<!-- ГЛАВА 10: ПОЖЕЛАНИЯ И БЛАГОДАРНОСТЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава десятая</div>
        <h2 class="chapter-title">Пожелания и благодарность</h2>
    </div>
    
    <div class="memoir-text">{chapters['gratitude_wishes']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[9]}" alt="Благодарность"></div><div class="photo-caption">Оставайся таким же прекрасным, {full_name}</div></div>' if len(processed_images) > 9 else f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Благодарность"></div><div class="photo-caption">Оставайся таким же прекрасным, {full_name}</div></div>' if processed_images else ''}
    
    <div class="memoir-finale">
        <div class="memoir-signature">
            Написано с любовью специально для {full_name}<br>
            <em>Твой тайный поклонник</em>
        </div>
        
        <div class="memoir-meta">
            Книга создана с помощью Mythic<br>
            "Каждый человек заслуживает красивых слов о себе"
        </div>
    </div>
</div>

</body>
</html>"""
    
    return html

def create_zine_html(content: dict, analysis: dict, images: list[Path]) -> str:
    """Создает HTML для мозаичного зина"""
    username = analysis.get('username', 'неизвестный')
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Зин @{username}</title>
    <style>
    body {{
            font-family: 'Arial', sans-serif;
            background: #f5f5f5;
        margin: 0;
            padding: 20px;
        }}
        .zine-container {{
        max-width: 800px;
        margin: 0 auto;
        background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .zine-title {{
            font-size: 2.5rem;
        text-align: center;
            margin-bottom: 2rem;
            color: #333;
        }}
        .zine-content {{
        line-height: 1.8;
        font-size: 1.1rem;
            color: #444;
        }}
        .photo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        margin: 2rem 0;
        }}
        .photo-card {{
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .photo-card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
    }}
    </style>
</head>
<body>
    <div class="zine-container">
        <h1 class="zine-title">{content.get('title', f'Зин @{username}')}</h1>
        <div class="zine-content">
            <p>{content.get('prologue', 'Здесь начинается история...')}</p>
            <p>{content.get('emotions', 'Эмоции и переживания...')}</p>
            <p>{content.get('places', 'Места и локации...')}</p>
            <p>{content.get('community', 'Сообщество и отклики...')}</p>
            <p>{content.get('legacy', 'Что остается в памяти...')}</p>
</div>

        <div class="photo-grid">
            {''.join([f'<div class="photo-card"><img src="data:image/jpeg;base64,placeholder" alt="Фото"></div>' for _ in range(min(6, len(images)))])}
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
    """
    Выделяет ключевые фразы только жирным шрифтом, максимум 10 выделений на текст.
    """
    highlight_words = [
        r'люблю', r'восхищаюсь', r'красота', r'улыбка', r'вдохновение', r'нежность', r'счастье',
        r'особый', r'магия', r'мечта', r'свет', r'душа', r'сердце', r'навсегда', r'благодарю',
        r'ты', r'твой', r'твоя', r'тебя', r'мир', r'жизнь', r'чувства', r'эмоции', r'вдохновляешь',
        r'улыбка', r'глаза', r'взгляд', r'обожаю', r'нежно', r'искренне', r'светишься', r'особенная', r'особенный'
    ]
    
    max_bold = 10
    bold_count = 0
    def highlight(match):
        nonlocal bold_count
        if bold_count < max_bold:
            bold_count += 1
            return f'<b>{match.group(0)}</b>'
        else:
            return match.group(0)
    
    pattern = re.compile(r'(' + '|'.join(highlight_words) + r')', re.IGNORECASE)
    formatted_text = pattern.sub(highlight, text)
    return formatted_text

