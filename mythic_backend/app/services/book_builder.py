import json
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from app.services.llm_client import strip_cliches, analyze_photo_for_memoir, generate_memoir_chapter
from typing import List, Tuple
import random

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
        
        # Ждем загрузки изображений и собираем их
        actual_images = []
        if images_dir.exists():
            # Собираем все изображения из папки
            for img_file in sorted(images_dir.glob("*")):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    actual_images.append(img_file)
        
        print(f"💕 Создаем {book_format} книгу для профиля")
        print(f"📸 Найдено {len(actual_images)} фотографий в {images_dir}")
        
        # Анализируем профиль
        analysis = analyze_profile_data(posts_data)
        
        # Генерируем контент в зависимости от формата
        if book_format == "zine":
            # Мозаичный зин - короткий контент
            content = generate_zine_content(analysis, actual_images)
            html = create_zine_html(content, analysis, actual_images)
        else:
            # Литературная Instagram-книга от первого лица
            content = {"format": "literary"}  # Передаем минимум данных
            html = create_literary_instagram_book_html(content, analysis, actual_images)
        
        # Сохраняем только HTML файл
        out = Path("data") / run_id
        out.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем HTML файл
        html_file = out / "book.html"
        html_file.write_text(html, encoding="utf-8")
        
        print(f"✅ {book_format.title()} книга создана!")
        print(f"📖 HTML версия: {out / 'book.html'}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании книги: {e}")
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
                    <h1>📖 Книга</h1>
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
            
            print(f"✅ Создана базовая HTML версия: {out / 'book.html'}")
            
        except Exception as final_error:
            print(f"❌ Критическая ошибка: {final_error}")

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
        
        # Добавляем grain (безопасно)
        try:
            noise = np.random.randint(0, 15, (img.size[1], img.size[0], 3), dtype=np.uint8)
            noise_img = Image.fromarray(noise, 'RGB').convert('RGBA')
            noise_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            noise_overlay.paste(noise_img, (0, 0))
            img = Image.alpha_composite(img, noise_overlay)
        except Exception as noise_error:
            print(f"❌ Ошибка при добавлении шума: {noise_error}")
        
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
                
                print(f"📸 Карточка {i+1}/15 ({card_type}): {card_content[:40]}...")
            except Exception as e:
                print(f"❌ Ошибка создания карточки {img_path}: {e}")
    
    # Если фото меньше 3, создаем минимальный зин
    if len(valid_images) < 3:
        print(f"⚠️ Мало фото для полноценного зина: {len(valid_images)}")
    
    print(f"✅ Обработано {len(valid_images)} фотографий из {len(images)} доступных")
    
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
    
    try:
        # 1. ЗАВЯЗКА - дневниковая запись (максимум 3 предложения)
        hook = generate_memoir_chapter(scene_mapping["hook"], scene_data)
        content['prologue'] = strip_cliches(hook)
        print(f"✅ Завязка: {hook[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка завязки: {e}")
        content['prologue'] = f"Наткнулся на @{username} случайно. Что-то зацепило."
    
    try:
        # 2. КОНФЛИКТ - SMS-стиль (максимум 4 строки)
        conflict = generate_memoir_chapter(scene_mapping["conflict"], scene_data)
        content['emotions'] = strip_cliches(conflict)
        print(f"✅ Конфликт: {conflict[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка конфликта: {e}")
        content['emotions'] = f"— {real_captions[0] if real_captions else 'Все хорошо'}\n— Но глаза говорят другое."
    
    try:
        # 3. ПОВОРОТ - момент озарения (максимум 3 предложения)
        turn = generate_memoir_chapter(scene_mapping["turn"], scene_data)
        content['places'] = strip_cliches(turn)
        print(f"✅ Поворот: {turn[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка поворота: {e}")
        content['places'] = f"Один кадр из {locations[0] if locations else 'неизвестного места'} изменил все. Здесь пахло честностью."
    
    try:
        # 4. КУЛЬМИНАЦИЯ - цитаты комментариев
        climax = generate_memoir_chapter(scene_mapping["climax"], scene_data)
        content['community'] = strip_cliches(climax)
        print(f"✅ Кульминация: {climax[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка кульминации: {e}")
        content['community'] = f"{followers} человек отреагировали:\n— Наконец-то ты показал себя настоящего\n— Спасибо за честность"
    
    try:
        # 5. ЭПИЛОГ - приглашение (максимум 2 предложения)
        epilogue = generate_memoir_chapter(scene_mapping["epilogue"], scene_data)
        content['legacy'] = strip_cliches(epilogue)
        print(f"✅ Эпилог: {epilogue[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка эпилога: {e}")
        content['legacy'] = "Листаю ленту в поиске нового дикого цветка. А вдруг это будешь ты?"
    
    # Метаданные
    content['title'] = f"Зин @{username}"
    content['photo_cards'] = photo_cards
    content['valid_images_count'] = len(valid_images)
    content['reading_time'] = "5 минут"
    
    return content

def create_literary_instagram_book_html(content: dict, analysis: dict, images: list[Path]) -> str:
    """Создает HTML романтическую книгу-мемуар от первого лица в стиле личного дневника"""
    
    # Фиксированные данные
    username = analysis.get('username', 'незнакомец')
    full_name = analysis.get('full_name', username)
    followers = analysis.get('followers', 0)
    following = analysis.get('following', 0)
    posts_count = analysis.get('posts_count', 0)
    bio = analysis.get('bio', '')
    
    # Реальные подписи и данные
    real_captions = analysis.get('captions', [])[:6]
    common_hashtags = analysis.get('common_hashtags', [])[:5]
    locations = analysis.get('locations', [])[:3]
    
    # Обрабатываем изображения (максимум 6 для каждой главы)
    processed_images = []
    for i, img_path in enumerate(images[:6]):
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
    
    # Анализируем фотографии для каждой главы мемуаров
    memoir_data = {
        'username': username,
        'followers': followers,
        'following': following,
        'posts_count': posts_count,
        'bio': bio,
        'captions': real_captions,
        'locations': locations,
        'common_hashtags': common_hashtags
    }
    
    # Генерируем все 6 глав мемуаров
    chapters = {}
    
    # Глава 1: Встреча
    try:
        chapters['meeting'] = generate_memoir_chapter("meeting", memoir_data)
        print("✅ Глава 1 'Встреча' создана")
    except Exception as e:
        print(f"❌ Ошибка главы 'Встреча': {e}")
        chapters['meeting'] = f"Поздним вечером я листал ленту Instagram и наткнулся на профиль @{username}. В свете экрана его лицо казалось вырезанным из старинной киноплёнки — загадочным и притягательным. 'Что-то здесь не так,' — подумал я, чувствуя запах остывшего кофе на столе. За окном шумел ночной город, но внимание поглотил этот незнакомый мир в квадратном кадре."
    
    # Глава 2: Первое впечатление (с анализом фото)
    try:
        photo_analysis = ""
        if processed_images:
            photo_analysis = analyze_photo_for_memoir(images[0], f"@{username}", "first_impression")
        chapters['first_impression'] = generate_memoir_chapter("first_impression", memoir_data, photo_analysis)
        print("✅ Глава 2 'Первое впечатление' создана")
    except Exception as e:
        print(f"❌ Ошибка главы 'Первое впечатление': {e}")
        caption = real_captions[0] if real_captions else "Момент жизни"
        chapters['first_impression'] = f"Первая фотография поразила меня игрой света и тени. '{caption}' — было написано под снимком, и эти слова зазвучали в моей голове, как мелодия. Я мог почти услышать шелест листьев, который, казалось, сопровождал этот кадр. 'Кто этот человек, который умеет так ловить красоту?' — думал я, разглядывая каждую деталь. Фотография пахла дождём и свободой."
    
    # Глава 3: История одного кадра
    try:
        chapters['story_creation'] = generate_memoir_chapter("story_creation", memoir_data)
        print("✅ Глава 3 'История одного кадра' создана")
    except Exception as e:
        print(f"❌ Ошибка главы 'История одного кадра': {e}")
        location = locations[0] if locations else "кафе на тихой улице"
        chapters['story_creation'] = f"Представляю, как создавался один из снимков. {username} шёл по {location}, когда свет упал именно так, как нужно. Он остановился, достал телефон — и в этот момент время замерло. 'Сейчас или никогда,' — прошептал он, нажимая на затвор.\n\nВ кадре запечатлелся не просто момент, а состояние души. Можно было почувствовать вкус воздуха, услышать далёкую музыку из окна.\n\nПозже, загружая фото, он понимал: это не просто картинка. Это приглашение другим увидеть мир его глазами."
    
    # Глава 4: Социальный анализ
    try:
        chapters['social_analysis'] = generate_memoir_chapter("social_analysis", memoir_data)
        print("✅ Глава 4 'Социальный анализ' создана")
    except Exception as e:
        print(f"❌ Ошибка главы 'Социальный анализ': {e}")
        chapters['social_analysis'] = f"{followers} подписчиков — не толпа, а сообщество единомышленников. В комментариях я читал: 'Наконец-то что-то настоящее в этом море фальши.' Эти люди искали подлинность, как я сейчас. 'Мы все устали от идеальности,' — понял я, прокручивая ленту. В цифровую эпоху искренность стала роскошью."
    
    # Глава 5: Между строк
    try:
        chapters['between_lines'] = generate_memoir_chapter("between_lines", memoir_data)
        print("✅ Глава 5 'Между строк' создана")
    except Exception as e:
        print(f"❌ Ошибка главы 'Между строк': {e}")
        chapters['between_lines'] = f"За идеальными кадрами @{username} я чувствовал настоящую жизнь. Не ту, что пахнет студийным светом, а ту, что пахнет утренним кофе и недосказанностью. 'Что он НЕ показывает?' — спрашивал я себя. Усталость в глазах, сомнения в 3 утра, радость от простых вещей. Мы носим маски даже в Instagram, но у некоторых маски прозрачные. Сквозь фильтры пробивается душа — и это прекрасно."
    
    # Глава 6: Прощальный портрет
    try:
        chapters['farewell_portrait'] = generate_memoir_chapter("farewell_portrait", memoir_data)
        print("✅ Глава 6 'Прощальный портрет' создана")
    except Exception as e:
        print(f"❌ Ошибка главы 'Прощальный портрет': {e}")
        chapters['farewell_portrait'] = f"Изучив профиль @{username}, я понял — красота живёт в деталях, которые мы обычно пропускаем. Желаю тебе сохранить этот редкий дар видеть необычное в обычном. Спасибо за урок внимательности к миру. Наши пути пересеклись в цифровом пространстве, как две кометы в бесконечности. В эпоху селфи и лайков ты напомнил: настоящее искусство — это честность."
    
    # Генерируем название книги
    book_titles = [
        f"Дневник о @{username}",
        f"Мемуары незнакомца",
        f"Встреча в Instagram",
        f"Романтические заметки о {username}",
        f"История одного профиля"
    ]
    book_title = random.choice(book_titles)
    
    # HTML в стиле романтических мемуаров
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
    
    /* Обложка мемуаров */
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
        content: '«';
        position: absolute;
        left: -25px;
        top: 2rem;
        font-size: 3rem;
        color: var(--accent);
        font-family: 'Playfair Display', serif;
    }}
    
    .cover-epigraph::after {{
        content: '»';
        position: absolute;
        right: -25px;
        bottom: 2rem;
        font-size: 3rem;
        color: var(--accent);
        font-family: 'Playfair Display', serif;
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
    
    /* Параграфы мемуаров */
    .memoir-paragraph {{
        text-align: justify;
        text-indent: 2.5rem;
        margin-bottom: 2.5rem;
        line-height: 1.9;
        font-size: 1.1rem;
    }}
    
    .memoir-paragraph.first {{
        text-indent: 0;
        font-weight: 500;
        font-size: 1.2rem;
    }}
    
    .memoir-text {{
        white-space: pre-line;
        text-align: justify;
        line-height: 1.9;
        font-size: 1.1rem;
    }}
    
    /* Цитаты и диалоги */
    .quote {{
        font-style: italic;
        color: var(--accent);
        text-indent: 0;
        margin: 2rem 0;
        padding: 1.5rem 2rem;
        background: var(--warm-cream);
        border-left: 4px solid var(--accent);
        border-radius: 8px;
        position: relative;
    }}
    
    .quote::before {{
        content: '"';
        position: absolute;
        left: 0.5rem;
        top: 0.8rem;
        font-size: 2rem;
        color: var(--accent);
        font-family: 'Playfair Display', serif;
    }}
    
    .inner-voice {{
        font-style: italic;
        color: var(--soft-ink);
        text-align: center;
        margin: 2rem 0;
        padding: 1rem;
        background: #f7f5f0;
        border-radius: 12px;
        text-indent: 0;
        border: 1px dashed var(--gold);
    }}
    
    /* Изображения в мемуарах */
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
        content: '– ';
        color: var(--accent);
        font-weight: bold;
    }}
    
    /* Финальная страница */
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

<!-- ОБЛОЖКА МЕМУАРОВ -->
<div class="memoir-page cover-memoir">
    <h1 class="cover-title">{book_title}</h1>
    <p class="cover-subtitle">Романтические мемуары от первого лица</p>
    
    <div class="cover-epigraph">
        Каждая фотография — окно в чью-то душу,<br>
        а каждый профиль — неоконченная история,<br>
        ждущая своего читателя
    </div>
    
    <div class="memoir-author">
        <strong>О профиле:</strong> @{username}<br>
        <small>{full_name}</small><br>
        <small>{followers:,} подписчиков • {posts_count} публикаций</small>
    </div>
</div>

<!-- ОГЛАВЛЕНИЕ -->
<div class="memoir-page">
    <div class="table-of-contents">
        <h2 class="toc-title">Оглавление</h2>
        
        <div class="toc-item">
            <span class="toc-chapter">Глава I. Встреча</span>
            <span class="toc-page">стр. 3</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава II. Первое впечатление</span>
            <span class="toc-page">стр. 4</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава III. История одного кадра</span>
            <span class="toc-page">стр. 5</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава IV. Углубляясь в детали</span>
            <span class="toc-page">стр. 6</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава V. Социальный анализ</span>
            <span class="toc-page">стр. 7</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава VI. Психологический портрет</span>
            <span class="toc-page">стр. 8</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава VII. География души</span>
            <span class="toc-page">стр. 9</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава VIII. Между строк</span>
            <span class="toc-page">стр. 10</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава IX. Музыка фотографий</span>
            <span class="toc-page">стр. 11</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава X. Отражения и размышления</span>
            <span class="toc-page">стр. 12</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Глава XI. Прощальный портрет</span>
            <span class="toc-page">стр. 13</span>
        </div>
        <div class="toc-item">
            <span class="toc-chapter">Эпилог. Что остается</span>
            <span class="toc-page">стр. 14</span>
        </div>
    </div>
</div>

<!-- ГЛАВА 1: ВСТРЕЧА -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава первая</div>
        <h2 class="chapter-title">Встреча</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('meeting', 'Поздним вечером я листал ленту Instagram...')}
    </div>
</div>

<!-- ГЛАВА 2: ПЕРВОЕ ВПЕЧАТЛЕНИЕ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава вторая</div>
        <h2 class="chapter-title">Первое впечатление</h2>
    </div>
    
    {'<div class="memoir-photo"><div class="photo-frame"><img src="' + processed_images[0] + '" alt="Первое впечатление"></div><div class="photo-caption">' + (real_captions[0] if real_captions else 'Первая фотография, которая зацепила меня') + '</div></div>' if processed_images else ''}
    
    <div class="memoir-text">
        {chapters.get('first_impression', 'Первая фотография поразила меня игрой света и тени...')}
    </div>
</div>

<!-- ГЛАВА 3: ИСТОРИЯ ОДНОГО КАДРА -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава третья</div>
        <h2 class="chapter-title">История одного кадра</h2>
    </div>
    
    {'<div class="memoir-photo"><div class="photo-frame"><img src="' + processed_images[1] + '" alt="Кадр с историей"></div><div class="photo-caption">' + (real_captions[1] if len(real_captions) > 1 else 'За каждым кадром — целая жизнь') + '</div></div>' if len(processed_images) > 1 else ''}
    
    <div class="memoir-text">
        {chapters.get('story_creation', 'Представляю, как создавался один из снимков...')}
    </div>
</div>

<!-- ГЛАВА 4: УГЛУБЛЯЯСЬ В ДЕТАЛИ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава четвёртая</div>
        <h2 class="chapter-title">Углубляясь в детали</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('deeper_details', 'Чем дольше я изучал профиль, тем больше замечал повторяющиеся мотивы...')}
    </div>
    
    {'<div class="memoir-photo"><div class="photo-frame"><img src="' + processed_images[2] + '" alt="Детали стиля"></div></div>' if len(processed_images) > 2 else ''}
</div>

<!-- ГЛАВА 5: СОЦИАЛЬНЫЙ АНАЛИЗ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава пятая</div>
        <h2 class="chapter-title">Социальный анализ</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('social_analysis', f'Аудитория @{username} — это не случайная толпа...')}
    </div>
    
    <div class="quote">
        Наконец-то что-то настоящее в этом море фальши
        <br><small>— из комментариев подписчиков</small>
    </div>
</div>

<!-- ГЛАВА 6: ПСИХОЛОГИЧЕСКИЙ ПОРТРЕТ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава шестая</div>
        <h2 class="chapter-title">Психологический портрет</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('psychological_portrait', 'Выбор сюжетов многое говорил о характере...')}
    </div>
    
    {'<div class="memoir-photo"><div class="photo-frame"><img src="' + processed_images[3] + '" alt="Психология в кадре"></div></div>' if len(processed_images) > 3 else ''}
</div>

<!-- ГЛАВА 7: ГЕОГРАФИЯ ДУШИ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава седьмая</div>
        <h2 class="chapter-title">География души</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('geography_soul', 'Места, которые выбирал для съёмок, складывались в карту его души...')}
    </div>
    
    {'<div class="memoir-photo"><div class="photo-frame"><img src="' + processed_images[4] + '" alt="Любимые места"></div></div>' if len(processed_images) > 4 else ''}
</div>

<!-- ГЛАВА 8: МЕЖДУ СТРОК -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава восьмая</div>
        <h2 class="chapter-title">Между строк</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('between_lines', f'За идеальными кадрами @{username} я чувствовал настоящую жизнь...')}
    </div>
    
    <div class="inner-voice">
        <em>Мы носим маски даже в Instagram, но у некоторых маски прозрачные...</em>
    </div>
</div>

<!-- ГЛАВА 9: МУЗЫКА ФОТОГРАФИЙ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава девятая</div>
        <h2 class="chapter-title">Музыка фотографий</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('music_photography', 'Фотографии звучали. Не метафорически, а буквально...')}
    </div>
    
    {'<div class="memoir-photo"><div class="photo-frame"><img src="' + processed_images[5] + '" alt="Визуальная музыка"></div></div>' if len(processed_images) > 5 else ''}
</div>

<!-- ГЛАВА 10: ОТРАЖЕНИЯ И РАЗМЫШЛЕНИЯ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава десятая</div>
        <h2 class="chapter-title">Отражения и размышления</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('reflections_changes', 'Изучение профиля изменило меня...')}
    </div>
    
    <div class="inner-voice">
        <em>Цепная реакция красоты — один человек замечает прекрасное, делится им, и это вдохновляет других...</em>
    </div>
</div>

<!-- ГЛАВА 11: ПРОЩАЛЬНЫЙ ПОРТРЕТ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава одиннадцатая</div>
        <h2 class="chapter-title">Прощальный портрет</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('farewell_portrait', f'Попытаясь создать цельный портрет @{username}...')}
    </div>
    
    <div class="quote">
        {real_captions[-1] if real_captions else 'В эпоху селфи и лайков ты напомнил: настоящее искусство — это честность'}
    </div>
</div>

<!-- ЭПИЛОГ -->
<div class="memoir-page">
    <div class="chapter-header">
        <div class="chapter-number">Эпилог</div>
        <h2 class="chapter-title">Что остается</h2>
    </div>
    
    <div class="memoir-text">
        {chapters.get('epilogue', 'В цифровую эпоху такие встречи приобретают особое значение...')}
    </div>
    
    <div class="memoir-finale">
        <div class="memoir-signature">
            С благодарностью за встречу<br>
            и урок красоты,<br>
            <em>романтический наблюдатель</em>
        </div>
    </div>
    
    <div class="memoir-meta">
        <strong>@{username}</strong><br>
        {followers:,} подписчиков • {following:,} подписок • {posts_count} публикаций<br>
        {f'«{bio}»<br>' if bio else ''}
        <br>
        <em>Мемуары написаны {random.choice(['тихим вечером', 'поздней ночью', 'на рассвете'])} в {random.choice(['январе', 'феврале', 'марте'])} 2024 года</em><br>
        <em>Локации: {", ".join(locations[:3]) if locations else "неизвестные места сердца"}</em><br>
        <em>Анализировано {len(processed_images)} фотографий из {len(images)} доступных</em>
    </div>
</div>

</body>
</html>"""
    
    return html

