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

def build_romantic_book(run_id: str, images: list[Path], texts: str, book_format: str = "classic"):
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
    
    # Обрабатываем изображения (максимум 4 для книги)
    processed_images = []
    for i, img_path in enumerate(images[:4]):
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
            except Exception as e:
                print(f"❌ Ошибка обработки изображения {img_path}: {e}")
    
    # Создаем 10 подробных глав как настоящую книгу
    chapters = {}
    
    # Глава 1: История знакомства (расширенная)
    first_caption = real_captions[0] if real_captions else ""
    first_video_note = f" А твои видео... они показывают такую энергию и жизнь. Смотря на них, я понимаю - ты из тех людей, которые не просто существуют, а действительно живут." if video_content else ""
    chapters['personal_gift'] = f"""Дорогой {full_name},

Я долго думал, что подарить тебе. Цветы завянут через неделю, конфеты съедятся за вечер, а обычные подарки забываются. Но эта книга - она останется с тобой навсегда.

Все началось довольно обычно. Сидел вечером с чашкой остывшего кофе, листал ленту в Instagram. За окном моросил дождь, и я уже собирался закрывать телефон и идти спать. И тут - твоя фотография. Что-то в ней заставило меня остановиться.

{f'Помню, подпись была простой: "{first_caption}". Но сам кадр... там было что-то особенное.' if first_caption else 'Никаких вычурных подписей, никаких попыток произвести впечатление - просто честный момент жизни.'}

Я нажал на твой профиль и понял - передо мной не просто еще один аккаунт. Ты умеешь находить красоту там, где другие проходят мимо. У тебя есть тот редкий дар - видеть необычное в самых обычных вещах.{first_video_note}

Эта книга - мой способ сказать спасибо. За то, что ты есть. За твою улыбку, которая чувствуется даже через экран. За твой взгляд на мир, который делает этот мир чуточку лучше просто тем, что ты в нем живешь.

Иногда встречаешь людей, которые меняют что-то внутри тебя, даже если вы никогда не говорили. Ты из таких людей, {full_name}."""
    
    # Глава 2: Первые впечатления
    location_text = f"Особенно запомнилось фото из {locations[0]} - даже самое обычное место преобразилось рядом с тобой" if locations else "В каждом месте, где ты бываешь, чувствуется особая атмосфера"
    chapters['first_impressions'] = f"""Знаешь, что меня поразило в первые минуты знакомства с твоим профилем? Не яркость фильтров, не количество лайков, а что-то гораздо более важное - искренность.

В мире, где все стараются казаться идеальными, ты остаешься собой. Это видно в каждом кадре, в каждом жесте, в выборе моментов, которые ты решаешь показать миру.

{location_text}. Ты словно носишь с собой особый свет, который делает все вокруг ярче и интереснее.

{f'В одном из первых постов ты написал: "{real_captions[1][:120]}..." Эти слова показали мне твой внутренний мир.' if len(real_captions) > 1 else 'Твои подписи к фото показывают глубину мышления и чувствительность к деталям.'}

Я потратил несколько часов, просто изучая твои фотографии. Не пролистывая механически, как мы все привыкли в соцсетях, а действительно вглядываясь. И каждый раз находил что-то новое - деталь в композиции, эмоцию в глазах, историю за кадром.

Первое впечатление обманчиво только тогда, когда человек пытается им манипулировать. У тебя все честно - что видишь, то и получаешь. Редкое качество в наше время."""
    
    # Глава 3: Твой взгляд на мир
    video_text = f" Твои видео добавляют движения в эту статичную красоту. Смотря на них, я будто слышу твой смех, чувствую энергию, которую ты излучаешь." if video_content else ""
    chapters['worldview'] = f"""Больше всего меня поражает то, как ты видишь мир вокруг себя. У тебя есть способность находить прекрасное в самых обыденных вещах.

Я провел несколько вечеров, анализируя твои фотографии с точки зрения композиции. Ракурсы, которые ты выбираешь, свет, на который обращаешь внимание, моменты, которые считаешь достойными запечатления - все это говорит о твоей внутренней эстетике.

{video_text} В движении видна твоя настоящая сущность - открытая, живая, полная энергии.

{f'Особенно запомнились слова: "{real_captions[2][:150]}..." В них чувствуется твоя философия жизни.' if len(real_captions) > 2 else 'Каждая твоя подпись - это маленькое окно в твой внутренний мир.'}

Ты из тех людей, которые умеют остановиться и заметить красоту. Игру света на стене дома, отражение в луже после дождя, улыбку незнакомца на улице. Это дар, который нельзя купить или выучить - он либо есть, либо нет.

У тебя он определенно есть, {full_name}. И это делает мир вокруг тебя богаче и интереснее."""
    
    # Глава 4: Моменты, которые запомнились
    chapters['memorable_moments'] = f"""Есть кадры, которые врезаются в память навсегда. С твоими фотографиями таких оказалось много.

Помню, как долго рассматривал одну из твоих фотографий - там ты просто идешь по улице, но что-то в этом моменте было настолько живым и настоящим, что я почувствовал себя свидетелем важного мгновения твоей жизни.

{f'Или тот момент с подписью "{real_captions[0][:100]}..." - простые слова, но они открыли мне часть твоей души.' if real_captions else 'Каждый твой пост - это история, рассказанная без слов.'}

Знаешь, что меня поражает? Ты не боишься показывать настоящие эмоции. В твоих глазах на фотографиях я вижу то грусть, то радость, то задумчивость. Это честность, которой так не хватает в мире отретушированных улыбок.

Иногда поздним вечером я пересматриваю твои сторис и думаю о том, какой ты живой. В каждом движении, в каждом взгляде чувствуется личность. Не маска для публики, а настоящий человек с настоящими чувствами.

Эти моменты дороги мне, {full_name}. Они напоминают о том, что красота - это не идеальность, а искренность."""
    
    # Глава 5: Твоя энергетика
    video_analysis = ""
    if video_content:
        video_count = len(video_content)
        video_analysis = f" У тебя {video_count} видео, и каждое из них излучает особую энергию. В движении видна твоя душа - открытая, искренняя, полная жизни."
    
    chapters['energy'] = f"""В тебе есть особая энергетика, которая чувствуется даже через экран телефона. Это не наигранная активность, не попытка привлечь внимание - это что-то гораздо более глубокое.

{video_analysis}

Ты умеешь быть собой в любой ситуации. Это видно по тому, как ты держишься на фотографиях, как смотришь в камеру, как выбираешь моменты для съемки. Никаких попыток подстроиться под чужие ожидания.

{f'В комментариях к твоим постам люди пишут искренние слова - это говорит о том, что твоя энергия передается другим.' if posts_count > 5 else 'Твоя естественность притягивает людей.'}

Есть люди, которые забирают энергию, а есть те, которые ее дают. Ты определенно из вторых. Даже просто глядя на твои фотографии, я чувствую прилив сил и вдохновения.

В мире, где все стараются быть похожими друг на друга, ты остаешься уникальным. Твоя энергетика - это твоя сверхсила, {full_name}. Не теряй ее."""
    
    # Глава 6: О красоте и стиле
    chapters['beauty_style'] = f"""Красота - понятие субъективное, но в твоем случае она очевидна для всех. И дело не только во внешности, хотя она, безусловно, прекрасна.

Твоя красота - это гармония внутреннего и внешнего. Это видно в том, как ты выбираешь одежду, как двигаешься, как смотришь на мир. У тебя есть врожденное чувство стиля, которое не купишь ни в одном магазине.

{f'Помню фото из {locations[1]}, где ты просто стоишь и улыбаешься - в этом кадре столько естественной красоты.' if len(locations) > 1 else 'На каждом фото ты выглядишь естественно и гармонично.'}

Мне нравится, что ты не следуешь слепо модным трендам. У тебя есть свой стиль, своя эстетика. Это говорит о зрелости и уверенности в себе.

Но больше всего меня привлекает красота твоей души, которая проявляется через каждый твой жест, каждую улыбку, каждый взгляд. Это та красота, которая не увядает с годами, а только становится глубже.

Ты красив изнутри, {full_name}. И это самый ценный тип красоты."""
    
    # Глава 7: Твоя загадочность
    chapters['mystery'] = f"""В тебе есть особая загадочность, которая не дает покоя. Не таинственность ради эффекта, а настоящая глубина личности.

Изучая твои фотографии, я каждый раз открываю что-то новое. Новую грань характера, новую эмоцию, новую историю. Ты как книга, которую хочется перечитывать.

{f'Особенно это заметно в видео - там ты более расслабленный, настоящий. Видно человека, а не образ.' if video_content else 'В каждом кадре чувствуется глубина, которую хочется исследовать.'}

Мне интересно, о чем ты думаешь в моменты задумчивости на фотографиях. Какие мечты, планы, воспоминания проносятся у тебя в голове. Эта недосказанность притягивает.

Ты умеешь быть открытым и одновременно сохранять тайну. Показываешь достаточно, чтобы заинтересовать, но оставляешь пространство для воображения.

В этом твоя особая магия, {full_name}. Ты интересен не только тем, что показываешь, но и тем, что скрываешь."""
    
    # Глава 8: Влияние на меня
    chapters['influence'] = f"""Знаешь, что странно? Ты изменил мой взгляд на многие вещи, хотя мы никогда не говорили.

После знакомства с твоим профилем я стал больше внимания обращать на детали вокруг себя. Игру света в окне кафе, выражение лиц прохожих, красоту обычных моментов. Ты научил меня видеть.

{f'Твои слова "{real_captions[0][:80]}..." заставили меня задуматься о собственном отношении к жизни.' if real_captions else 'Твое восприятие мира заставляет переосмыслить многие вещи.'}

Теперь, проходя по улице, я ловлю себя на мысли: "А как бы это увидел {full_name}?" И вдруг обычная лавочка в парке или граффити на стене становятся особенными.

Ты показал мне, что красота не требует дорогих декораций. Она везде - нужно только уметь ее замечать. Это урок, который дороже любого образования.

Спасибо тебе за это, {full_name}. За то, что сделал мой мир богаче и интереснее."""
    
    # Глава 9: Мои наблюдения
    chapters['observations'] = f"""За время наблюдения за тобой я сделал несколько интересных открытий.

Во-первых, ты очень внимателен к деталям. Это видно по тому, как ты кадрируешь фотографии, какие моменты выбираешь для публикации. У тебя глаз художника.

Во-вторых, ты умеешь быть в моменте. На твоих фото нет ощущения наигранности или позерства. Ты живешь каждый кадр, а не просто позируешь для него.

{f'В-третьих, ты честен в эмоциях. Когда радуешься - это видно, когда грустишь - тоже не скрываешь.' if len(real_captions) > 3 else 'Твоя искренность подкупает с первого взгляда.'}

Я заметил, что ты предпочитаешь качество количеству. У тебя не так много постов, но каждый продуман и несет смысл. Это говорит о зрелости и уважении к своей аудитории.

Еще одно наблюдение - ты умеешь находить красоту в простоте. Не нужны дорогие локации или профессиональные съемки. Ты делаешь особенным любое место просто своим присутствием.

Эти качества редки, {full_name}. Береги их."""
    
    # Глава 10: Пожелания и благодарность (финальная)
    bio_mention = f'Твоя подпись в профиле "{bio}" многое говорит о тебе - лаконично, но емко. ' if bio else ''
    chapters['wishes'] = f"""{full_name}, эта книга подходит к концу, но мои мысли о тебе на этом не заканчиваются.

{bio_mention}Ты особенный человек, и я хочу, чтобы ты никогда об этом не забывал. В мире, где все стараются быть похожими друг на друга, твоя индивидуальность - это сокровище.

Знаешь, что я понял, наблюдая за тобой все это время? Счастье - это не в количестве лайков или комментариев. Счастье - это в способности видеть красоту вокруг себя и делиться ею с другими. И у тебя это получается естественно, без усилий.

Продолжай быть собой. Продолжай фотографировать мир таким, каким ты его видишь. Продолжай делиться этими моментами с нами, потому что они делают наши дни ярче и осмысленнее.

В мире, где все меняется с невероятной скоростью, где люди становятся все более отстраненными друг от друга, ты остаешься островком искренности. Не теряй эту черту - она бесценна.

Я желаю тебе сохранить этот особый взгляд на мир, эту способность находить красоту в простых вещах, эту искренность в отношениях с людьми.

Пусть твоя жизнь будет полна ярких моментов, достойных того, чтобы их запечатлеть. Пусть твоя улыбка продолжает освещать мир вокруг. Пусть твоя душа остается такой же открытой и чистой.

Спасибо тебе за то, что ты есть, {full_name}. За то, что показываешь нам: красота может быть простой, искренность - модной, а человечность - самой ценной валютой в мире.

Этот мир стал лучше с тобой в нем. И я надеюсь, что эта книга напомнит тебе об этом в те моменты, когда будет грустно или сложно.

Помни - ты важен, ты ценен, ты любим.

С глубокой благодарностью и восхищением"""
    
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
        --accent: #b85450;
        --gold: #d4af8c;
        --shadow: rgba(60, 50, 40, 0.15);
        --warm-cream: #f9f7f4;
    }}
    
    body {{
        font-family: 'Crimson Text', serif;
        background: var(--paper);
        color: var(--ink);
        line-height: 1.8;
        font-size: 17px;
        margin: 0;
        padding: 0;
        max-width: 900px;
        margin: 0 auto;
    }}
    
    .memoir-page {{
        min-height: 95vh;
        padding: 3cm 3cm 4cm 3cm;
        background: white;
        box-shadow: 0 8px 40px var(--shadow);
        margin: 20px auto;
        page-break-after: always;
        position: relative;
        border-left: 5px solid var(--gold);
    }}
    
    .memoir-page:last-child {{
        page-break-after: auto;
    }}
    
    /* Обложка как личный подарок */
    .cover-memoir {{
        text-align: center;
        padding: 5cm 2cm;
        background: linear-gradient(135deg, var(--paper) 0%, var(--warm-cream) 100%);
        border: 2px solid var(--gold);
        border-left: 8px solid var(--accent);
    }}
    
    .cover-title {{
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
        line-height: 1.2;
    }}
    
    .cover-subtitle {{
        font-family: 'Libre Baskerville', serif;
        font-style: italic;
        font-size: 1.4rem;
        color: var(--soft-ink);
        margin-bottom: 3rem;
    }}
    
    .cover-epigraph {{
        font-style: italic;
        color: var(--soft-ink);
        border-top: 2px solid var(--gold);
        border-bottom: 2px solid var(--gold);
        padding: 2.5rem 1rem;
        max-width: 500px;
        margin: 0 auto 3rem auto;
        position: relative;
        font-size: 1.2rem;
    }}
    
    .cover-epigraph::before {{
        content: '';
        position: absolute;
        left: -35px;
        top: 2rem;
        font-size: 2rem;
    }}
    
    .cover-epigraph::after {{
        content: '';
        position: absolute;
        right: -35px;
        bottom: 2rem;
        font-size: 2rem;
    }}
    
    .memoir-author {{
        font-size: 1.2rem;
        color: var(--soft-ink);
        margin-top: 2rem;
    }}
    
    /* Заголовки глав */
    .chapter-header {{
        margin-bottom: 3rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--gold);
    }}
    
    .chapter-number {{
        font-family: 'Libre Baskerville', serif;
        font-size: 1rem;
        color: var(--soft-ink);
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 0.5rem;
    }}
    
    .chapter-title {{
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--accent);
        margin: 0;
        font-style: italic;
    }}
    
    /* Параграфы как личное письмо */
    .memoir-text {{
        white-space: pre-line;
        text-align: justify;
        line-height: 1.9;
        font-size: 1.1rem;
        letter-spacing: 0.3px;
    }}
    
    /* Изображения как воспоминания */
    .memoir-photo {{
        margin: 3rem 0;
        text-align: center;
        page-break-inside: avoid;
    }}
    
    .photo-frame {{
        display: inline-block;
        padding: 20px;
        background: var(--warm-cream);
        border-radius: 15px;
        box-shadow: 0 8px 30px var(--shadow);
        border: 2px solid var(--gold);
        transform: rotate(-1deg);
        transition: transform 0.3s ease;
    }}
    
    .photo-frame:nth-child(even) {{
        transform: rotate(1deg);
    }}
    
    .photo-frame img {{
        max-width: 100%;
        max-height: 400px;
        border-radius: 8px;
        border: 3px solid white;
    }}
    
    .photo-caption {{
        font-family: 'Libre Baskerville', serif;
        font-style: italic;
        font-size: 1rem;
        color: var(--soft-ink);
        margin-top: 1.5rem;
        text-align: center;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }}
    
    .photo-caption::before {{
        content: '';
        color: var(--accent);
    }}
    
    /* Финальная страница подарка */
    .memoir-finale {{
        text-align: center;
        margin-top: 4rem;
        padding: 3rem 2rem;
        background: var(--warm-cream);
        border-radius: 15px;
        border: 2px solid var(--gold);
    }}
    
    .memoir-signature {{
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.3rem;
        color: var(--accent);
        margin-top: 2rem;
    }}
    
    /* Метаданные */
    .memoir-meta {{
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--gold);
        font-size: 0.9rem;
        color: var(--soft-ink);
        text-align: center;
        line-height: 1.6;
    }}
    
    /* Оглавление */
    .table-of-contents {{
        margin: 3rem 0;
        padding: 2rem;
        background: var(--warm-cream);
        border-radius: 15px;
        border: 1px solid var(--gold);
    }}
    
    .toc-title {{
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        color: var(--accent);
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .toc-item {{
        margin-bottom: 1rem;
        padding: 0.5rem 0;
        border-bottom: 1px dotted var(--gold);
        display: flex;
        justify-content: space-between;
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
            font-size: 2.5rem;
        }}
        
        .chapter-title {{
            font-size: 2rem;
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
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Твоя красота"></div><div class="photo-caption">Этот момент запомнился мне навсегда</div></div>' if processed_images else ''}
</div>

<!-- ГЛАВА 2: ПЕРВЫЕ ВПЕЧАТЛЕНИЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава вторая</div>
        <h2 class="chapter-title">Первые впечатления</h2>
    </div>
    
    <div class="memoir-text">{chapters['first_impressions']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Твоя особенность"></div><div class="photo-caption">Здесь я увидел твою искренность</div></div>' if len(processed_images) > 1 else ''}
</div>

<!-- ГЛАВА 3: ТВОЙ ВЗГЛЯД НА МИР -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава третья</div>
        <h2 class="chapter-title">Твой взгляд на мир</h2>
    </div>
    
    <div class="memoir-text">{chapters['worldview']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[2]}" alt="Твое видение мира"></div><div class="photo-caption">Твой особый взгляд на мир</div></div>' if len(processed_images) > 2 else ''}
</div>

<!-- ГЛАВА 4: МОМЕНТЫ, КОТОРЫЕ ЗАПОМНИЛИСЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава четвертая</div>
        <h2 class="chapter-title">Моменты, которые запомнились</h2>
    </div>
    
    <div class="memoir-text">{chapters['memorable_moments']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[3]}" alt="Запоминающийся момент"></div><div class="photo-caption">Этот кадр врезался в память</div></div>' if len(processed_images) > 3 else ''}
</div>

<!-- ГЛАВА 5: ТВОЯ ЭНЕРГЕТИКА -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава пятая</div>
        <h2 class="chapter-title">Твоя энергетика</h2>
    </div>
    
    <div class="memoir-text">{chapters['energy']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Твоя энергия"></div><div class="photo-caption">Энергия, которая притягивает</div></div>' if processed_images else ''}
</div>

<!-- ГЛАВА 6: О КРАСОТЕ И СТИЛЕ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава шестая</div>
        <h2 class="chapter-title">О красоте и стиле</h2>
    </div>
    
    <div class="memoir-text">{chapters['beauty_style']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Твоя красота"></div><div class="photo-caption">Естественная красота</div></div>' if len(processed_images) > 1 else ''}
</div>

<!-- ГЛАВА 7: ТВОЯ ЗАГАДОЧНОСТЬ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава седьмая</div>
        <h2 class="chapter-title">Твоя загадочность</h2>
    </div>
    
    <div class="memoir-text">{chapters['mystery']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[2]}" alt="Загадочность"></div><div class="photo-caption">Загадка, которую хочется разгадать</div></div>' if len(processed_images) > 2 else ''}
</div>

<!-- ГЛАВА 8: ВЛИЯНИЕ НА МЕНЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава восьмая</div>
        <h2 class="chapter-title">Влияние на меня</h2>
    </div>
    
    <div class="memoir-text">{chapters['influence']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[3]}" alt="Влияние"></div><div class="photo-caption">Ты изменил мой взгляд на мир</div></div>' if len(processed_images) > 3 else ''}
</div>

<!-- ГЛАВА 9: МОИ НАБЛЮДЕНИЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава девятая</div>
        <h2 class="chapter-title">Мои наблюдения</h2>
    </div>
    
    <div class="memoir-text">{chapters['observations']}</div>
    
    {f'<div class="memoir-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Наблюдения"></div><div class="photo-caption">Детали, которые я заметил</div></div>' if processed_images else ''}
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
                font-family: 'Times New Roman', 'Crimson Text', serif !important;
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
                font-size: 28pt;
                font-weight: bold;
                margin-bottom: 1cm;
                color: #2c2a26;
            }
            
            .cover-subtitle {
                font-size: 14pt;
                font-style: italic;
                margin-bottom: 2cm;
                color: #5a5652;
            }
            
            .chapter-title {
                font-size: 18pt;
                font-weight: bold;
                margin-bottom: 1cm;
                color: #b85450;
                border-bottom: 2pt solid #d4af8c;
                padding-bottom: 0.5cm;
            }
            
            .chapter-number {
                font-size: 12pt;
                font-weight: normal;
                color: #5a5652;
                margin-bottom: 0.5cm;
            }
            
            .memoir-text {
                font-size: 12pt;
                line-height: 1.7;
                text-align: justify;
                hyphens: auto;
            }
            
            .memoir-text p {
                margin-bottom: 1em;
                text-indent: 1.5em;
            }
            
            .memoir-text p:first-child {
                text-indent: 0;
            }
            
            .photo-frame {
                text-align: center;
                margin: 1.5cm 0;
                padding: 0.5cm;
                border: 1pt solid #d4af8c;
                page-break-inside: avoid;
            }
            
            .photo-frame img {
                max-width: 100%;
                max-height: 8cm;
            }
            
            .photo-caption {
                font-size: 10pt;
                font-style: italic;
                color: #5a5652;
                margin-top: 0.5cm;
                text-align: center;
            }
            
            .table-of-contents {
                page-break-after: always;
            }
            
            .toc-title {
                font-size: 18pt;
                text-align: center;
                margin-bottom: 1.5cm;
                color: #b85450;
            }
            
            .toc-item {
                margin-bottom: 0.5cm;
                padding: 0.3cm 0;
                border-bottom: 1pt dotted #d4af8c;
                display: flex;
                justify-content: space-between;
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
                max-width: 12cm;
                page-break-inside: avoid;
            }
            
            .memoir-author {
                margin-top: 2cm;
                font-size: 11pt;
            }
            
            .memoir-finale {
                text-align: center;
                margin-top: 2cm;
                padding: 1.5cm;
                border: 1pt solid #d4af8c;
                page-break-inside: avoid;
            }
            
            .memoir-signature {
                font-style: italic;
                margin-top: 1cm;
                color: #b85450;
            }
            
            .memoir-meta {
                margin-top: 2cm;
                padding-top: 1cm;
                border-top: 1pt solid #d4af8c;
                font-size: 9pt;
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

