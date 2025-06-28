import json
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from app.services.llm_client import strip_cliches, analyze_photo_for_memoir, generate_memoir_chapter
from typing import List, Tuple
import random

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
            create_pdf_from_html(html, pdf_file)
            print(f"📄 PDF версия создана: {pdf_file}")
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
    
    if images:
        # Умная логика выбора фотографий
        selected_indices = []
        total_images = len(images)
        
        if total_images >= 4:
            # Если много фото - берем первое, из середины, ближе к концу, последнее
            selected_indices = [
                0,  # первое
                total_images // 3,  # треть от начала
                (total_images * 2) // 3,  # две трети
                total_images - 1  # последнее
            ]
        elif total_images >= 2:
            # Если мало фото - берем первое и последнее
            selected_indices = [0, total_images - 1]
            # Добавляем средние если есть
            if total_images >= 3:
                selected_indices.insert(1, total_images // 2)
            if total_images >= 4:
                selected_indices.insert(2, total_images - 2)
        else:
            # Если совсем мало - берем что есть
            selected_indices = list(range(total_images))
        
        print(f"📸 Умный выбор фото: из {total_images} беру позиции {selected_indices}")
        
        # Анализируем первое фото для определения пола
        if images and images[0].exists():
            print("🔍 Анализирую фото для определения пола...")
            detected_gender = analyze_photo_for_gender(images[0])
            print(f"✅ Определен пол: {detected_gender}")
        
        for i in selected_indices:
            img_path = images[i]
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
                        print(f"✅ Обработано фото #{i+1}")
                except Exception as e:
                    print(f"❌ Ошибка обработки изображения {img_path}: {e}")
    
    # Подготавливаем контекст для ИИ
    context_data = {
        'username': username,
        'full_name': full_name,
        'followers': followers,
        'posts_count': posts_count,
        'bio': bio,
        'captions': real_captions[:5],  # Первые 5 подписей
        'locations': locations[:3],     # Первые 3 локации
        'video_content': video_content[:3],  # Первые 3 видео
        'has_videos': len(video_content) > 0
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
            'key': 'personal_gift',
            'title': 'История знакомства',
            'prompt': f"""Напиши главу о знакомстве с {full_name} через Instagram.
            
            ПОЛ: {gender} ({'девушка' if gender == 'female' else 'парень'}) - используй "{she_he}", "{her_his}"
            
            НАЧНИ С УТРА/ДНЯ (НЕ ВЕЧЕРА!): "Утром за кофе...", "В обеденный перерыв...", "Выходным днем..."
            
            ПРОСТОЙ ВЛЮБЛЕННЫЙ ТОНЕ:
            - "Когда я увидел {her_his}, сердце забилось быстрее"
            - "{she_he.capitalize()} сразу понравилась мне"
            - "Я влюбился в {her_his} с первого взгляда"
            - НЕ используй "Не могу поверить!" и "Потрясающе!" - слишком много!
            
            РЕАЛЬНЫЕ ДАННЫЕ:
            - Имя: {full_name}
            - Username: @{username}  
            - Подписчики: {followers}
            - Реальная подпись: "{real_captions[0] if real_captions else 'без подписи'}"
            
            ПРОСТЫЕ КОМПЛИМЕНТЫ:
            - "{she_he.capitalize()} красивая" или "{she_he} симпатичный"
            - "Мне понравился {her_his} стиль"
            - "Классные фотографии"
            - Пиши просто и искренне!
            
            АНАЛИЗИРУЙ ПОСТЫ ПРОСТО:
            - Что {she_he} постит в Instagram
            - Какие подписи пишет
            - Что меня зацепило
            
            Тон: влюбленный, простой, читабельный. 3-4 абзаца."""
        },
        {
            'key': 'first_impressions', 
            'title': 'Первые впечатления',
            'prompt': f"""Напиши о первом впечатлении от {full_name}.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ ПО-ДРУГОМУ: "В кафе листая ленту...", "После работы...", "Воскресным утром..."
            
            ПРОСТЫЕ КОМПЛИМЕНТЫ:
            - "{she_he.capitalize()} красивая"
            - "У {her_his} хороший вкус в фото"
            - "Мне нравится как {she_he} выглядит"
            - НЕ перебарщивай с восклицаниями!
            
            РЕАЛЬНЫЕ НАБЛЮДЕНИЯ:
            - Какие фото у {her_his}
            - Локации: {locations[:2] if locations else ['разные места']}
            - Стиль постов: {real_post_analysis[0]['type'] if real_post_analysis else 'фото'}
            
            ПРОСТЫЕ МЫСЛИ:
            - Что именно понравилось
            - Почему зацепило
            - Какие эмоции вызвало
            
            Стиль: влюбленный, простой, искренний. 3-4 абзаца."""  
        },
        {
            'key': 'worldview',
            'title': 'Твой взгляд на мир',
            'prompt': f"""Напиши о характере {full_name} влюбленным взглядом.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ ОРИГИНАЛЬНО: "Листая {her_his} профиль...", "Изучая {her_his} посты...", "Смотря на {her_his} фото..."
            
            ПРОСТОЙ АНАЛИЗ:
            - "Мне нравится {her_his} характер"
            - "У {her_his} хороший вкус"
            - "{she_he.capitalize()} интересная личность"
            
            АНАЛИЗИРУЙ ПОСТЫ:
            - Что постит: {real_post_analysis[0]['type'] if real_post_analysis else 'фото'}
            - Подписи: "{real_captions[1] if len(real_captions) > 1 else 'короткие'}"
            - Где фотографируется: {locations[0] if locations else 'разные места'}
            
            ПРОСТЫЕ ВЫВОДЫ:
            - Что в характере понравилось
            - Какие качества привлекли
            - Почему именно {she_he}
            
            Тон: влюбленный, простой, читабельный. 3-4 абзаца."""
        },
        {
            'key': 'memorable_moments',
            'title': 'Моменты, которые запомнились',
            'prompt': f"""Напиши о постах {full_name}, которые запомнились.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ СВЕЖО: "Вспоминаю {her_his} пост...", "Один кадр особенно запомнился...", "Есть фото которое зацепило..."
            
            ПРОСТЫЕ ВОСПОМИНАНИЯ:
            - "Этот пост понравился"
            - "Я запомнил это фото"
            - "Этот момент зацепил"
            
            КОНКРЕТНЫЙ ПОСТ:
            - Пост: "{real_post_analysis[0]['caption'] if real_post_analysis else 'интересная подпись'}"
            - Локация: {real_post_analysis[0]['location'] if real_post_analysis and real_post_analysis[0]['location'] else 'без геолокации'}
            - Лайки: {real_post_analysis[0]['likes'] if real_post_analysis else 'немного'} лайков
            
            ЧТО ПОНРАВИЛОСЬ:
            - Что конкретно зацепило
            - Какие эмоции вызвало
            - Почему запомнилось
            
            Стиль: влюбленный, простой, естественный. 3-4 абзаца."""
        },
        {
            'key': 'energy',
            'title': 'Твоя энергетика',
            'prompt': f"""Напиши об энергетике {full_name}.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ ПО-НОВОМУ: "У {her_his} особая энергия...", "Чувствую {her_his} настроение через экран...", "В {her_his} постах есть что-то..."
            
            ПРОСТЫЕ ОЩУЩЕНИЯ:
            - "{her_his.capitalize()} энергия мне нравится"
            - "Чувствую {her_his} тепло"
            - "{she_he.capitalize()} излучает позитив"
            
            АНАЛИЗ ПОСТОВ:
            - Как часто постит: {posts_count} постов
            - Что передают фотографии
            - Какая аура чувствуется
            
            ПРОСТЫЕ ВЫВОДЫ:
            - Как {her_his} энергия влияет на меня
            - Что особенного в {her_his} ауре
            - Почему эта энергетика привлекает
            
            Тон: влюбленный, простой, искренний. 3-4 абзаца."""
        },
        {
            'key': 'beauty_style',
            'title': 'О красоте и стиле',
            'prompt': f"""Напиши о красоте {full_name}.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ ОРИГИНАЛЬНО: "Каждый раз смотря на {her_his}...", "{she_he.capitalize()} умеет красиво фотографироваться...", "В {her_his} есть особая красота..."
            
            ПРОСТЫЕ КОМПЛИМЕНТЫ:
            - "{she_he.capitalize()} красивая"
            - "У {her_his} хороший стиль"
            - "Мне нравится как {she_he} выглядит"
            - "Фотогеничная" или "Фотогеничный"
            
            О ВНЕШНОСТИ:
            - Что в внешности нравится
            - Какие черты привлекают
            - Как стиль отражает личность
            
            ПРОСТЫЕ МЫСЛИ:
            - Пиши как влюбленный но не переборщи
            - Каждая деталь должна быть приятной
            - Искренние чувства к {her_his} красоте
            
            Тон: влюбленный, простой, приятный. 3-4 абзаца."""
        },
        {
            'key': 'mystery',
            'title': 'Твоя загадочность',
            'prompt': f"""Напиши о загадочности {full_name}.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ ИНТЕРЕСНО: "В {her_his} есть какая-то тайна...", "{she_he.capitalize()} загадочная личность...", "Хочется узнать {her_his} лучше..."
            
            ПРОСТОЕ ЛЮБОПЫТСТВО:
            - "{she_he.capitalize()} интригует меня"
            - "В {her_his} есть что-то загадочное"
            - "Хочется узнать {her_his} секреты"
            
            ЧТО ИНТРИГУЕТ:
            - Что скрывается за красотой
            - О чем думает этот человек
            - Какие у {her_his} мечты
            
            ПРОСТАЯ ЗАГАДОЧНОСТЬ:
            - Желание узнать ближе
            - Что хочется понять
            - Какие тайны хочется разделить
            
            Тон: влюбленный, любопытный, простой. 3-4 абзаца."""
        },
        {
            'key': 'influence',
            'title': 'Влияние на меня',
            'prompt': f"""Напиши как {full_name} повлияла на меня.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ ЧЕСТНО: "После знакомства с {her_his}...", "{she_he.capitalize()} изменила мой взгляд...", "Благодаря {her_his}..."
            
            ПРОСТАЯ БЛАГОДАРНОСТЬ:
            - "{she_he.capitalize()} изменила мою жизнь"
            - "Стал по-другому смотреть на вещи"
            - "Открыл для себя новые эмоции"
            
            РЕАЛЬНЫЕ ИЗМЕНЕНИЯ:
            - Как изменилось восприятие
            - Что нового появилось в жизни
            - Какие чувства пробудились
            
            ПРОСТАЯ РОМАНТИКА:
            - Благодарность за влюбленность
            - Как любовь изменила жизнь
            - Что дала эта встреча
            
            Тон: влюбленный, благодарный, простой. 3-4 абзаца."""
        },
        {
            'key': 'observations',
            'title': 'Мои наблюдения',
            'prompt': f"""Напиши наблюдения о {full_name}.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ НАБЛЮДАТЕЛЬНО: "Заметил что {she_he}...", "Наблюдая за {her_his} профилем...", "Изучая {her_his} привычки..."
            
            ПРОСТЫЕ НАБЛЮДЕНИЯ:
            - "Изучаю каждую {her_his} деталь"
            - "Замечаю интересные особенности"
            - "Наблюдаю за {her_his} постами"
            
            КОНКРЕТНЫЕ ЗАМЕЧАНИЯ:
            - Как ведет профиль: {posts_count} постов
            - Что особенного в поведении
            - Какие привычки заметил
            
            ПРОСТЫЕ ВЫВОДЫ:
            - Что говорят наблюдения о характере
            - Какие качества особенно дороги
            - Почему это привлекает
            
            Тон: влюбленный, внимательный, простой. 3-4 абзаца."""
        },
        {
            'key': 'wishes',
            'title': 'Пожелания и благодарность',
            'prompt': f"""Напиши финальные слова для {full_name}.
            
            ПОЛ: {gender} - используй "{she_he}", "{her_his}"
            
            НАЧНИ ТЕПЛО: "В заключение хочу сказать...", "Завершая эту книгу...", "На прощание..."
            
            ПРОСТЫЕ ПОЖЕЛАНИЯ:
            - "Хочу чтобы {she_he} была счастлива"
            - "Пусть у {her_his} все будет хорошо"
            - "{she_he.capitalize()} заслуживает самого лучшего"
            
            БЛАГОДАРНОСТЬ:
            - За то что познакомился
            - За красоту которая вдохновляет
            - За чувства которые подарила
            
            ПРОСТОЙ ФИНАЛ:
            - Слова любви и восхищения
            - Пожелания на будущее
            - Финальное признание
            
            Тон: влюбленный, теплый, искренний. 4-5 абзацев."""
        }
    ]
    
    # Генерируем каждую главу через ИИ
    for config in chapter_configs:
        try:
            print(f"💝 Генерирую главу '{config['title']}' для {full_name}...")
            
            # Используем существующую функцию генерации мемуаров
            generated_content = generate_memoir_chapter("romantic_book_chapter", {
                'prompt': config['prompt'],
                'context': context_data,
                'style': 'romantic_personal_gift'
            })
            
            # Очищаем от клише
            clean_content = strip_cliches(generated_content)
            chapters[config['key']] = clean_content
            
            print(f"✅ Глава '{config['title']}' готова")
            
        except Exception as e:
            print(f"💔 Ошибка генерации главы '{config['title']}': {e}")
            # Fallback с минимальным контентом
            chapters[config['key']] = f"Дорогой {full_name}, эта глава посвящена твоей особенной природе. Ты удивительный человек, и это видно в каждом твоем посте."
    
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
    
    <div class="memoir-text">{chapters['personal_gift']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Твоя красота"></div><div class="photo-caption">В этом взгляде - целая вселенная</div></div>' if processed_images else ''}
</div>

<!-- ГЛАВА 2: ПЕРВЫЕ ВПЕЧАТЛЕНИЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава вторая</div>
        <h2 class="chapter-title">Первые впечатления</h2>
    </div>
    
    <div class="memoir-text">{chapters['first_impressions']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Твоя особенность"></div><div class="photo-caption">Красота, которая не нуждается в словах</div></div>' if len(processed_images) > 1 else ''}
</div>

<!-- ГЛАВА 3: ТВОЙ ВЗГЛЯД НА МИР -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава третья</div>
        <h2 class="chapter-title">Твой взгляд на мир</h2>
    </div>
    
    <div class="memoir-text">{chapters['worldview']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[2]}" alt="Твое видение мира"></div><div class="photo-caption">Сияние души, которое видно даже через экран</div></div>' if len(processed_images) > 2 else ''}
</div>

<!-- ГЛАВА 4: МОМЕНТЫ, КОТОРЫЕ ЗАПОМНИЛИСЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава четвертая</div>
        <h2 class="chapter-title">Моменты, которые запомнились</h2>
    </div>
    
    <div class="memoir-text">{chapters['memorable_moments']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[3]}" alt="Запоминающийся момент"></div><div class="photo-caption">Мгновение, которое хочется растянуть на вечность</div></div>' if len(processed_images) > 3 else ''}
</div>

<!-- ГЛАВА 5: ТВОЯ ЭНЕРГЕТИКА -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава пятая</div>
        <h2 class="chapter-title">Твоя энергетика</h2>
    </div>
    
    <div class="memoir-text">{chapters['energy']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Твоя энергия"></div><div class="photo-caption">Энергия света, что делает мир ярче</div></div>' if processed_images else ''}
</div>

<!-- ГЛАВА 6: О КРАСОТЕ И СТИЛЕ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава шестая</div>
        <h2 class="chapter-title">О красоте и стиле</h2>
    </div>
    
    <div class="memoir-text">{chapters['beauty_style']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Твоя красота"></div><div class="photo-caption">Гармония, созданная самой природой</div></div>' if len(processed_images) > 1 else ''}
</div>

<!-- ГЛАВА 7: ТВОЯ ЗАГАДОЧНОСТЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава седьмая</div>
        <h2 class="chapter-title">Твоя загадочность</h2>
    </div>
    
    <div class="memoir-text">{chapters['mystery']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[2]}" alt="Загадочность"></div><div class="photo-caption">Глубина, в которой хочется утонуть</div></div>' if len(processed_images) > 2 else ''}
</div>

<!-- ГЛАВА 8: ВЛИЯНИЕ НА МЕНЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава восьмая</div>
        <h2 class="chapter-title">Влияние на меня</h2>
    </div>
    
    <div class="memoir-text">{chapters['influence']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[3]}" alt="Влияние"></div><div class="photo-caption">Образ, что изменил мое восприятие мира</div></div>' if len(processed_images) > 3 else ''}
</div>

<!-- ГЛАВА 9: МОИ НАБЛЮДЕНИЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава девятая</div>
        <h2 class="chapter-title">Мои наблюдения</h2>
    </div>
    
    <div class="memoir-text">{chapters['observations']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Наблюдения"></div><div class="photo-caption">Совершенство в каждой детали</div></div>' if processed_images else ''}
</div>

<!-- ГЛАВА 10: ПОЖЕЛАНИЯ И БЛАГОДАРНОСТЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава десятая</div>
        <h2 class="chapter-title">Пожелания и благодарность</h2>
    </div>
    
    <div class="memoir-text">{chapters['wishes']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Финальное фото"></div><div class="photo-caption">Оставайся таким же прекрасным, {full_name}</div></div>' if len(processed_images) > 1 else ''}
    
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

def create_pdf_from_html(html_content: str, output_path: Path) -> Path:
    """Генерирует PDF из HTML контента используя weasyprint"""
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Создаем конфигурацию шрифтов
        font_config = FontConfiguration()
        
        # CSS стили специально для PDF с улучшенной типографикой
        pdf_css = CSS(string="""
            @page {
                size: A4;
                margin: 2cm;
                @top-center {
                    content: "";
                }
                @bottom-center {
                    content: counter(page);
                    font-family: 'Times New Roman', serif;
                    font-size: 10pt;
                    color: #666;
                }
            }
            
            body {
                font-family: 'Times New Roman', 'Georgia', serif !important;
                font-size: 12pt;
                line-height: 1.6;
                color: #2c2a26;
                margin: 0;
                padding: 0;
            }
            
            .memoir-page {
                padding: 1.5cm 1cm;
                margin: 0;
                min-height: unset;
                box-shadow: none;
                border: none;
                page-break-after: always;
            }
            
            .memoir-page:last-child {
                page-break-after: auto;
            }
            
            .cover-memoir {
                text-align: center;
                padding: 3cm 2cm;
                page-break-after: always;
            }
            
            .cover-title {
                font-size: 24pt;
                font-weight: bold;
                margin-bottom: 1cm;
                color: #2c2a26;
            }
            
            .cover-subtitle {
                font-size: 12pt;
                font-style: italic;
                margin-bottom: 2cm;
                color: #5a5652;
            }
            
            .chapter-title {
                font-size: 16pt;
                font-weight: bold;
                margin-bottom: 1cm;
                color: #8b4513;
                border-bottom: 1pt solid #d4af8c;
                padding-bottom: 0.5cm;
            }
            
            .chapter-number {
                font-size: 10pt;
                font-weight: normal;
                color: #5a5652;
                margin-bottom: 0.5cm;
            }
            
            .memoir-text {
                font-size: 11pt;
                line-height: 1.6;
                text-align: justify;
                hyphens: auto;
                margin-bottom: 1em;
            }
            
            .memoir-text p {
                margin-bottom: 1em;
                text-indent: 1.2em;
            }
            
            .memoir-text p:first-child {
                text-indent: 0;
            }
            
            .photo-frame {
                text-align: center;
                margin: 1cm 0;
                padding: 0.3cm;
                border: 1pt solid #d4af8c;
                page-break-inside: avoid;
            }
            
            .photo-frame img {
                max-width: 100%;
                max-height: 6cm;
            }
            
            .photo-caption {
                font-size: 9pt;
                font-style: italic;
                color: #5a5652;
                margin-top: 0.3cm;
                text-align: center;
            }
            
            .table-of-contents {
                page-break-after: always;
            }
            
            .toc-title {
                font-size: 16pt;
                text-align: center;
                margin-bottom: 1.5cm;
                color: #8b4513;
            }
            
            .toc-item {
                margin-bottom: 0.4cm;
                padding: 0.2cm 0;
                border-bottom: 1pt dotted #d4af8c;
                display: flex;
                justify-content: space-between;
                font-size: 10pt;
            }
            
            .toc-chapter {
                font-weight: bold;
            }
            
            .toc-page {
                color: #5a5652;
                font-style: italic;
            }
            
            .cover-epigraph {
                font-style: italic;
                border-top: 1pt solid #d4af8c;
                border-bottom: 1pt solid #d4af8c;
                padding: 1cm;
                margin: 2cm auto;
                max-width: 10cm;
                page-break-inside: avoid;
                font-size: 11pt;
            }
            
            .memoir-author {
                margin-top: 2cm;
                font-size: 10pt;
            }
            
            .memoir-finale {
                text-align: center;
                margin-top: 1.5cm;
                padding: 1cm;
                border: 1pt solid #d4af8c;
                page-break-inside: avoid;
            }
            
            .memoir-signature {
                font-style: italic;
                margin-top: 1cm;
                color: #8b4513;
                font-size: 11pt;
            }
            
            .memoir-meta {
                margin-top: 1.5cm;
                padding-top: 1cm;
                border-top: 1pt solid #d4af8c;
                font-size: 8pt;
                color: #5a5652;
                text-align: center;
            }
        """, font_config=font_config)
        
        # Генерируем PDF
        html_doc = HTML(string=html_content)
        pdf_doc = html_doc.render(stylesheets=[pdf_css], font_config=font_config)
        pdf_doc.write_pdf(output_path)
        
        print(f"✅ PDF книга создана: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Ошибка создания PDF: {e}")
        # Возвращаем путь даже если файл не создался, для обработки ошибок
        return output_path

