from pathlib import Path
import json
import random
import time
from app.services.llm_client import generate_memoir_chapter, strip_cliches, analyze_photo_for_memoir
from app.services.book_builder import analyze_profile_data, format_chapter_text, build_fantasy_book as _build_fantasy_book

def analyze_profile_for_fantasy(posts_data: list) -> dict:
    """Анализирует профиль для фэнтези-контекста"""
    if not posts_data:
        return {}
    
    profile = posts_data[0]
    analysis = {
        "username": profile.get("username", "Unknown"),
        "full_name": profile.get("fullName", ""),
        "bio": profile.get("biography", ""),
        "followers": profile.get("followersCount", 0),
        "posts": profile.get("latestPosts", []),
        "profile_pic": profile.get("profilePicUrl", ""),
    }
    
    # Анализируем для фэнтези-контекста
    analysis["hero_name"] = analysis["full_name"] or analysis["username"]
    analysis["realm_description"] = f"Королевство @{analysis['username']}"
    
    return analysis

def generate_fantasy_chapters(analysis: dict, images: list[Path]) -> dict:
    """Генерирует главы фэнтези-книги — коротко, читаемо, с fallback."""
    
    full_name = analysis.get("full_name", analysis.get("username", "Герой"))
    username = analysis.get("username", "hero")
    bio = analysis.get("bio", "")
    
    # Новое требование для фото
    photo_instruction = "В начале главы упомяни фото как магический артефакт, пророчество или символ (например: 'Этот кадр — как пророчество для великого героя!'), но дальше рассказывай о герое. Фото — только лёгкое вдохновение, не главный смысл. Пиши возвышенно, в стиле фэнтези, но живо и лично."
    
    # Фэнтези конфигурация глав - короткие и читаемые
    fantasy_configs = [
        {
            'key': 'prophecy',
            'title': 'Древнее пророчество',
            'prompt': f"""Напиши короткую главу \"Древнее пророчество\" о герое {full_name} (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        },
        {
            'key': 'magical_realm',
            'title': 'Магическое королевство',
            'prompt': f"""Напиши короткую главу \"Магическое королевство\" о мире героя {full_name} (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        },
        {
            'key': 'ancient_wisdom',
            'title': 'Древняя мудрость',
            'prompt': f"""Напиши короткую главу \"Древняя мудрость\" о знаниях героя {full_name} (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        },
        {
            'key': 'magical_artifacts',
            'title': 'Магические артефакты',
            'prompt': f"""Напиши короткую главу \"Магические артефакты\" о сокровищах героя {full_name} (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        },
        {
            'key': 'elemental_power',
            'title': 'Власть над стихиями',
            'prompt': f"""Напиши короткую главу \"Власть над стихиями\" о магических способностях {full_name} (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        },
        {
            'key': 'dragon_bond',
            'title': 'Союз с драконом',
            'prompt': f"""Напиши короткую главу \"Союз с драконом\" о магической связи {full_name} с древним драконом (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        },
        {
            'key': 'quest_calling',
            'title': 'Зов приключений',
            'prompt': f"""Напиши короткую главу \"Зов приключений\" о судьбе героя {full_name} (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        },
        {
            'key': 'legendary_deeds',
            'title': 'Легендарные подвиги',
            'prompt': f"""Напиши короткую главу \"Легендарные подвиги\" о великих делах {full_name} (1-2 абзаца, 60-80 слов). Стиль — личный, возвышенный фэнтези о человеке, с метафорами, но без сказочной мишуры. Коротко и эмоционально. {photo_instruction}"""
        }
    ]
    
    # Fallback-тексты для каждой главы
    quick_fallbacks = {
        'prophecy': f"Древние пророчества говорили о герое по имени {full_name}. Его судьба была предопределена звездами, а каждое его действие становилось частью великой легенды.",
        'magical_realm': f"Королевство @{username} раскинулось между мирами, где магия течет в каждом камне. {full_name} стал хранителем этого удивительного мира.",
        'ancient_wisdom': f"В глазах {full_name} читается мудрость веков. Он помнит времена Первой Магии и несет в себе знания древних предков.",
        'magical_artifacts': f"Каждый предмет в коллекции {full_name} излучает древнюю магию. Кристаллы силы, амулеты защиты и руны памяти хранят его секреты.",
        'elemental_power': f"Стихии повинуются {full_name} как древнему повелителю. Огонь, вода, земля и воздух гармонично сочетаются в его душе.",
        'dragon_bond': f"Древний дракон признал в {full_name} достойного союзника. Их магическая связь стала легендой, а совместные полеты над королевством восхищают всех.",
        'quest_calling': f"Судьба зовет {full_name} в великий поход. Знаки указывают путь, а спутники готовы следовать за героем до конца.",
        'legendary_deeds': f"Барды по всему королевству слагают песни о подвигах {full_name}. Его имя стало синонимом отваги и благородства."
    }
    
    chapters = {}
    
    for config in fantasy_configs:
        try:
            print(f"🧙‍♂️ Генерирую главу '{config['title']}'...")
            
            generated_content = generate_memoir_chapter("fantasy_chapter", {
                'prompt': config['prompt'],
                'style': 'epic_fantasy'
            })
            
            if len(generated_content.strip()) < 60:
                chapters[config['key']] = quick_fallbacks[config['key']]
            else:
                clean_content = strip_cliches(generated_content)
                chapters[config['key']] = format_chapter_text(clean_content)
                
        except Exception as e:
            print(f"❌ Ошибка генерации главы '{config['title']}': {e}")
            chapters[config['key']] = quick_fallbacks[config['key']]
    
    return chapters

def create_fantasy_html(analysis: dict, chapters: dict, images: list[Path]) -> str:
    """Создает HTML для фэнтези-книги"""
    
    full_name = analysis.get("full_name", analysis.get("username", "Герой"))
    username = analysis.get("username", "hero")
    
    # Обработка изображений - конвертируем в base64
    processed_images = []
    for i, img_path in enumerate(images[:9]):
        if img_path.exists():
            try:
                import base64
                with open(img_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    processed_images.append(f"data:image/jpeg;base64,{img_data}")
            except Exception as e:
                print(f"❌ Ошибка обработки изображения {img_path}: {e}")
    
    book_title = f"Хроники героя {full_name}"
    
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
    :root {{
        --accent-color: #333333;
        --background-color: #ffffff;
        --text-color: #333;
        --font-body: 'Playfair Display', serif;
        --font-caption: 'Open Sans', sans-serif;
        --fantasy-accent: #8b4513;
        --fantasy-secondary: #d4af37;
        --shadow-soft: rgba(0, 0, 0, 0.1);
    }}

    @page {{
        size: A5 portrait;
        margin: 2.5cm;
        
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
        box-shadow: none;
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
        padding: 0;
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
        padding: 0;
    }}

    .chapter-main-title {{
        font-family: var(--font-body);
        font-weight: bold;
        font-size: 32pt;
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
        initial-letter: 3;
        font-weight: bold;
        padding-right: 0.2em;
        color: var(--fantasy-accent);
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
        color: var(--fantasy-accent);
        margin: 2rem 0;
        font-family: serif;
    }}
    .final-signature {{
        margin-top: 1rem;
        font-size: 18pt;
        font-style: normal;
    }}

    /* Фэнтезийные акценты */
    .fantasy-accent {{
        color: var(--fantasy-accent);
    }}
    
    .fantasy-emoji {{
        font-size: 1.2em;
        margin: 0 0.2em;
        opacity: 0.7;
    }}

    @media screen {{
        body {{
            font-size: 16px;
        }}
        .book-page {{
            width: 148mm;
            min-height: 210mm;
            margin: 2rem auto;
            padding: 2.5cm;
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
        .chapter-subtitle {{ font-size: 14pt; }}
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
        <p class="cover-subtitle">Хроники героя</p>
        <div class="cover-separator"></div>
        <p class="cover-dedication">Эпическая сага о великом герое</p>
    </div>
</div>

<!-- Table of Contents -->
<div class="book-page toc-page">
    <h2 class="toc-title">Содержание</h2>
    <ul class="toc-list">
        <li class="toc-item">
            <a href="#chapter-prophecy" class="chapter-name">Глава 1 – Древнее пророчество</a>
            <span class="leader"></span>
            <a href="#chapter-prophecy" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-magical_realm" class="chapter-name">Глава 2 – Магическое королевство</a>
            <span class="leader"></span>
            <a href="#chapter-magical_realm" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-ancient_wisdom" class="chapter-name">Глава 3 – Древняя мудрость</a>
            <span class="leader"></span>
            <a href="#chapter-ancient_wisdom" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-magical_artifacts" class="chapter-name">Глава 4 – Магические артефакты</a>
            <span class="leader"></span>
            <a href="#chapter-magical_artifacts" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-elemental_power" class="chapter-name">Глава 5 – Власть над стихиями</a>
            <span class="leader"></span>
            <a href="#chapter-elemental_power" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-dragon_bond" class="chapter-name">Глава 6 – Союз с драконом</a>
            <span class="leader"></span>
            <a href="#chapter-dragon_bond" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-quest_calling" class="chapter-name">Глава 7 – Зов приключений</a>
            <span class="leader"></span>
            <a href="#chapter-quest_calling" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-legendary_deeds" class="chapter-name">Глава 8 – Легендарные подвиги</a>
            <span class="leader"></span>
            <a href="#chapter-legendary_deeds" class="page-ref"></a>
        </li>
    </ul>
</div>

<!-- Chapter Pages -->
<div id="chapter-prophecy" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 1</h3>
    <h2 class="chapter-main-title">Древнее пророчество</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[0]}" alt="Photo for Chapter 1" class="chapter-image">
        <p class="chapter-image-caption">🔮 Избранный судьбой 🔮</p>
    </div>
    """ if processed_images else ""}

    <div class="chapter-body">
        {chapters.get('prophecy', 'Древние пророчества говорили о великом герое...')}
    </div>
</div>

<div id="chapter-magical_realm" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 2</h3>
    <h2 class="chapter-main-title">Магическое королевство</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[1]}" alt="Photo for Chapter 2" class="chapter-image">
        <p class="chapter-image-caption">🏰 Правитель магических земель 🏰</p>
    </div>
    """ if len(processed_images) > 1 else ""}

    <div class="chapter-body">
        {chapters.get('magical_realm', 'Королевство магии раскинулось между мирами...')}
    </div>
</div>

<div id="chapter-ancient_wisdom" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 3</h3>
    <h2 class="chapter-main-title">Древняя мудрость</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[2]}" alt="Photo for Chapter 3" class="chapter-image">
        <p class="chapter-image-caption">🧙‍♂️ Носитель древних знаний 🧙‍♂️</p>
    </div>
    """ if len(processed_images) > 2 else ""}

    <div class="chapter-body">
        {chapters.get('ancient_wisdom', 'Мудрость веков живет в глазах героя...')}
    </div>
</div>

<div id="chapter-magical_artifacts" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 4</h3>
    <h2 class="chapter-main-title">Магические артефакты</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[3]}" alt="Photo for Chapter 4" class="chapter-image">
        <p class="chapter-image-caption">⚡ Повелитель древних сил ⚡</p>
    </div>
    """ if len(processed_images) > 3 else ""}

    <div class="chapter-body">
        {chapters.get('magical_artifacts', 'Древние артефакты хранят силу веков...')}
    </div>
</div>

<div id="chapter-elemental_power" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 5</h3>
    <h2 class="chapter-main-title">Власть над стихиями</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[4]}" alt="Photo for Chapter 5" class="chapter-image">
        <p class="chapter-image-caption">🔥💧🌍💨 Владыка четырех стихий 🔥💧🌍💨</p>
    </div>
    """ if len(processed_images) > 4 else ""}

    <div class="chapter-body">
        {chapters.get('elemental_power', 'Стихии повинуются воле героя...')}
    </div>
</div>

<div id="chapter-dragon_bond" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 6</h3>
    <h2 class="chapter-main-title">Союз с драконом</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[5]}" alt="Photo for Chapter 6" class="chapter-image">
        <p class="chapter-image-caption">🐲 Союзник древних драконов 🐲</p>
    </div>
    """ if len(processed_images) > 5 else ""}

    <div class="chapter-body">
        {chapters.get('dragon_bond', 'Древний дракон признал в герое равного...')}
    </div>
</div>

<div id="chapter-quest_calling" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 7</h3>
    <h2 class="chapter-main-title">Зов приключений</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[6]}" alt="Photo for Chapter 7" class="chapter-image">
        <p class="chapter-image-caption">⚔️ Странник судьбы ⚔️</p>
    </div>
    """ if len(processed_images) > 6 else ""}

    <div class="chapter-body">
        {chapters.get('quest_calling', 'Судьба зовет героя в великий поход...')}
    </div>
</div>

<div id="chapter-legendary_deeds" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 8</h3>
    <h2 class="chapter-main-title">Легендарные подвиги</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[7]}" alt="Photo for Chapter 8" class="chapter-image">
        <p class="chapter-image-caption">🎵 Герой легенд и баллад 🎵</p>
    </div>
    """ if len(processed_images) > 7 else ""}

    <div class="chapter-body">
        {chapters.get('legendary_deeds', 'Барды слагают песни о подвигах героя...')}
    </div>
</div>

<!-- Final Page -->
<div class="book-page final-page">
    <div class="final-content">
        <p>
            Вот и завершилась первая книга хроник о <span class="fantasy-accent">{full_name}</span>.
        </p>
        <p style="margin-top: 1.5em;">
            Великие хроники о {full_name} завершены, но эхо его деяний ещё долго будет звенеть в сердцах тех, кто услышал его зов.<br><br>
            <em>"Даже когда солнце скрыто за бурей,<br>
            даже когда тьма растекается по земле,<br>
            помните — неважно, насколько труден путь,<br>
            свет героя всегда найдёт дорогу."</em>
        </p>
        <div class="final-ornament">⚔️</div>
        <p>
            Легенда будет продолжена в новых главах! <span class="fantasy-emoji">🔮</span>
        </p>
        <div class="final-signature">
            Создано магией Mythic<br>
            <em>"Каждый достоин стать героем легенд"</em>
        </div>
    </div>
</div>

</body>
</html>"""
    
    return html



def build_fantasy_book(run_id, images, comments, book_format='classic', user_id=None):
    return _build_fantasy_book(run_id, images, comments, book_format, user_id) 