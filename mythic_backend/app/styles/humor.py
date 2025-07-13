from pathlib import Path
import json
import random
import time
from app.services.llm_client import generate_memoir_chapter, strip_cliches, analyze_photo_for_memoir
from app.services.book_builder import analyze_profile_data, format_chapter_text
import re

ROMANTIC_WORDS = re.compile(r"(нежн|романт|любов|искренн|я\\W+создан)", re.I)
SYSTEM_STANDUP = """
Ты — стендап-комик. Пиши ДЕРЗКО, с ПАНЧАМИ, как на сцене.
ИСПОЛЬЗУЙ:
• Абсурдные сравнения (колобок на электросамокате, Wi-Fi пароль от Вселенной)
• Современные отсылки (TikTok, Dolby Atmos, Excel-файлы)
• Обращение к залу («Зал, признайтесь», «Ребята»)
• Диалоги и внутренние монологи
• Гиперболу и неожиданные повороты

⚠️ ЗАПРЕЩЕНО:
• романтические интонации
• «искренне», «нежно», «тепло», «любовь», «я создан…»
• лирические отступления
• сентиментальность
• банальные описания

Если в тексте появляется хоть намёк на романтику — ОТВЕТ СЧИТАЕТСЯ ОШИБОЧНЫМ.
Пиши так, будто ты на сцене и нужно «рвать» зал.
""".strip()

def analyze_profile_for_humor(posts_data: list) -> dict:
    """Анализирует профиль для юмористического контекста"""
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
    
    # Определяем пол по имени и био
    full_name = analysis["full_name"].lower()
    bio = analysis["bio"].lower()
    
    # Простая логика определения пола
    female_indicators = ["девушка", "женщина", "она", "её", "красавица", "принцесса", "королева"]
    male_indicators = ["парень", "мужчина", "он", "его", "красавец", "принц", "король"]
    
    is_female = any(indicator in bio for indicator in female_indicators)
    is_male = any(indicator in bio for indicator in male_indicators)
    
    # Если не определили по био, пробуем по имени
    if not is_female and not is_male:
        # Простая эвристика по окончаниям имен
        female_endings = ["а", "я", "на", "ина", "ова", "ева"]
        male_endings = ["ов", "ев", "ин", "ый", "ой"]
        
        for ending in female_endings:
            if full_name.endswith(ending):
                is_female = True
                break
        for ending in male_endings:
            if full_name.endswith(ending):
                is_male = True
                break
    
    # По умолчанию считаем женским полом (для безопасности)
    analysis["gender"] = "female" if is_female or not is_male else "male"
    analysis["pronoun"] = "она" if analysis["gender"] == "female" else "он"
    analysis["pronoun_genitive"] = "её" if analysis["gender"] == "female" else "его"
    
    # Анализируем для юмористического контекста
    analysis["comedian_name"] = analysis["full_name"] or analysis["username"]
    analysis["stage_name"] = f"@{analysis['username']}"
    
    return analysis

def generate_humor_chapters(analysis: dict, images: list[Path]) -> dict:
    """Генерирует главы юмористической книги — коротко, структурировано, современно, с fallback."""
    from app.services.llm_client import generate_memoir_chapter, strip_cliches
    full_name = analysis.get("full_name", analysis.get("username", "Комик"))
    username = analysis.get("username", "comedian")
    bio = analysis.get("bio", "")

    # Новое требование для фото
    photo_instruction = "В начале главы коротко и с юмором упомяни фото (например: 'На этом фото ты выглядишь как...'), но дальше рассказывай историю о человеке. Фото — только лёгкое вдохновение, не главный смысл. Пиши как будто это личная история, а фото — просто повод для рассказа."

    # Конфиг глав: ключ, название, промпт
    humor_configs = [
        {
            'key': 'introduction',
            'title': 'Пролог: Знакомство с комиком',
            'prompt': f"""Напиши пролог (1-2 абзаца, 80-120 слов) 'Знакомство с комиком' о {full_name}. Стиль — лёгкий, современный, с иронией, личное обращение, без пошлости. Начни с фразы: 'Дорогие читатели, знакомьтесь — {full_name}!' Не повторяй пример, но держи стиль как в стендап-биографиях. {photo_instruction} Добавь пословицу: 'Смех — лучшее лекарство, а юмор — лучший друг'. Пиши как пролог к юмористическому роману."""
        },
        {
            'key': 'daily_comedy',
            'title': 'Глава первая: Комедия повседневности',
            'prompt': f"""Напиши первую главу (1-2 абзаца, 80-120 слов) 'Комедия повседневности' о {full_name}. Стиль — наблюдательный юмор, забавные детали, личные привычки, как будто рассказываешь другу. Не повторяй пример, но держи стиль как в стендапах о жизни. {photo_instruction} Добавь пословицу: 'Жизнь — это комедия для тех, кто умеет смеяться'. Пиши как главу юмористического романа."""
        },
        {
            'key': 'social_media_star',
            'title': 'Глава вторая: Звезда соцсетей',
            'prompt': f"""Напиши вторую главу (1-2 абзаца, 80-120 слов) 'Звезда соцсетей' о {full_name} и его Instagram. Стиль — современный юмор, интернет-мемы, лёгкие шутки, личное обращение. Не повторяй пример, но держи стиль как в блогах о соцсетях. {photo_instruction} Добавь пословицу: 'В интернете никто не знает, что ты кот, но все знают, что ты звезда'. Пиши как главу юмористического романа."""
        },
        {
            'key': 'unique_style',
            'title': 'Глава третья: Неповторимый стиль',
            'prompt': f"""Напиши третью главу (1-2 абзаца, 80-120 слов) 'Неповторимый стиль' о внешности и стиле {full_name}. Стиль — добрый юмор, без злых шуток, позитив, личное обращение. Не повторяй пример, но держи стиль как в блогах о моде с юмором. {photo_instruction} Добавь пословицу: 'Стиль — это когда ты выглядишь так, будто случайно попал в кадр, но на самом деле готовился час'. Пиши как главу юмористического романа."""
        },
        {
            'key': 'epilogue',
            'title': 'Эпилог: Финальные аплодисменты',
            'prompt': f"""Напиши эпилог (1-2 абзаца, 80-120 слов) 'Финальные аплодисменты' о {full_name}. Стиль — тёплый финал, благодарность, позитивные пожелания, личное обращение. Не повторяй пример, но держи стиль как в финале стендапа. {photo_instruction} Добавь пословицу: 'Спасибо за смех, который делает мир ярче'. Пиши как эпилог юмористического романа."""
        }
    ]

    # Fallback-тексты для каждой главы
    quick_fallbacks = {
        'introduction': f"{full_name} — человек, который может рассмешить даже будильник. Его жизнь — это стендап без перерыва на рекламу!",
        'daily_comedy': f"Обычный день {full_name} — это череда комичных ситуаций, где даже чайник смеётся первым.",
        'social_media_star': f"Instagram @{username} — место, где лайки ставят даже соседи по подъезду. Фото, мемы, позитив!",
        'unique_style': f"Стиль {full_name} — это как хорошая шутка: запоминается с первого взгляда!",
        'epilogue': f"Вот и подошла к концу наша весёлая история о {full_name}. Спасибо за смех и позитив!"
    }

    chapters = {}
    for config in humor_configs:
        try:
            generated_content = generate_memoir_chapter("humor_chapter", {
                'prompt': config['prompt'],
                'style': 'humorous_light'
            })
            if len(generated_content.strip()) < 60:
                chapters[config['key']] = quick_fallbacks[config['key']]
            else:
                clean_content = strip_cliches(generated_content)
                chapters[config['key']] = clean_content
        except Exception as e:
            print(f"❌ Ошибка генерации главы '{config['title']}': {e}")
            chapters[config['key']] = quick_fallbacks[config['key']]
    return chapters

def format_paragraphs(text):
    # Разбиваем по двойному или одинарному переносу строки и оборачиваем в <p>
    paragraphs = [f"<p>{p.strip()}</p>" for p in text.split('\n') if p.strip()]
    return "\n".join(paragraphs)

def create_humor_html(analysis: dict, chapters: dict, images: list[Path]) -> str:
    """Создает HTML для юмористической книги"""
    
    full_name = analysis.get("full_name", analysis.get("username", "Комик"))
    username = analysis.get("username", "comedian")
    
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
    
    book_title = f"Веселые истории о {full_name}"
    
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
        color: #555;
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
    <style>
    /* Книжная верстка: узкая колонка, переносы, номер страницы сверху */
    .chapter-body {
        max-width: 440px;
        margin: 0 auto;
        text-align: justify;
        line-height: 1.65;
        hyphens: auto;
    }
    .chapter-body p:first-of-type::first-letter{
        initial-letter: 2;
        font-weight: 700;
        padding-right: 0.15em;
    }
    .chapter-body p{
        margin: 0 0 1.2em;
    }
    @page{
        margin: 2.5cm;
        @top-center{
            content: counter(page);
            font-family: 'Playfair Display', serif;
            font-size: 14pt;
            color: #666;
        }
        @bottom-center{ content: ""; }
    }
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
        <li class="toc-item">
            <a href="#chapter-introduction" class="chapter-name">Глава 1 – Знакомство с комиком</a>
            <span class="leader"></span>
            <a href="#chapter-introduction" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-daily_comedy" class="chapter-name">Глава 2 – Комедия повседневности</a>
            <span class="leader"></span>
            <a href="#chapter-daily_comedy" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-social_media_star" class="chapter-name">Глава 3 – Звезда соцсетей</a>
            <span class="leader"></span>
            <a href="#chapter-social_media_star" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-photo_adventures" class="chapter-name">Глава 4 – Фотоприключения</a>
            <span class="leader"></span>
            <a href="#chapter-photo_adventures" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-unique_style" class="chapter-name">Глава 5 – Неповторимый стиль</a>
            <span class="leader"></span>
            <a href="#chapter-unique_style" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-funny_wisdom" class="chapter-name">Глава 6 – Мудрость с юмором</a>
            <span class="leader"></span>
            <a href="#chapter-funny_wisdom" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-social_butterfly" class="chapter-name">Глава 7 – Душа компании</a>
            <span class="leader"></span>
            <a href="#chapter-social_butterfly" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-creative_chaos" class="chapter-name">Глава 8 – Творческий хаос</a>
            <span class="leader"></span>
            <a href="#chapter-creative_chaos" class="page-ref"></a>
        </li>
        <li class="toc-item">
            <a href="#chapter-finale_applause" class="chapter-name">Глава 9 – Финальные аплодисменты</a>
            <span class="leader"></span>
            <a href="#chapter-finale_applause" class="page-ref"></a>
        </li>
    </ul>
</div>

<!-- Chapter Pages -->
<div id="chapter-introduction" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 1</h3>
    <h2 class="chapter-main-title">Знакомство с комиком</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[0]}" alt="Photo for Chapter 1" class="chapter-image">
        <p class="chapter-image-caption"><span class="emoji-colorful">😆</span> Наш главный герой в действии! <span class="emoji-colorful">🌟</span></p>
    </div>
    """ if processed_images else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('introduction', 'Знакомьтесь - наш главный герой!'))}
    </div>
</div>

<div id="chapter-daily_comedy" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 2</h3>
    <h2 class="chapter-main-title">Комедия повседневности</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[1]}" alt="Photo for Chapter 2" class="chapter-image">
        <p class="chapter-image-caption">😄 Обычный день необычного человека 😄</p>
    </div>
    """ if len(processed_images) > 1 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('daily_comedy', 'Каждый день - новая комедия!'))}
    </div>
</div>

<div id="chapter-social_media_star" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 3</h3>
    <h2 class="chapter-main-title">Звезда соцсетей</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[2]}" alt="Photo for Chapter 3" class="chapter-image">
        <p class="chapter-image-caption">📸 Мастер селфи и позитива 📸</p>
    </div>
    """ if len(processed_images) > 2 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('social_media_star', 'Instagram как источник веселья!'))}
    </div>
</div>

<div id="chapter-photo_adventures" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 4</h3>
    <h2 class="chapter-main-title">Фотоприключения</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[3]}" alt="Photo for Chapter 4" class="chapter-image">
        <p class="chapter-image-caption">🎪 Цирк в одном кадре 🎪</p>
    </div>
    """ if len(processed_images) > 3 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('photo_adventures', 'Каждое фото - приключение!'))}
    </div>
</div>

<div id="chapter-unique_style" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 5</h3>
    <h2 class="chapter-main-title">Неповторимый стиль</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[4]}" alt="Photo for Chapter 5" class="chapter-image">
        <p class="chapter-image-caption">✨ Икона стиля и хорошего настроения ✨</p>
    </div>
    """ if len(processed_images) > 4 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('unique_style', 'Стиль - это состояние души!'))}
    </div>
</div>

<div id="chapter-funny_wisdom" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 6</h3>
    <h2 class="chapter-main-title">Мудрость с юмором</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[5]}" alt="Photo for Chapter 6" class="chapter-image">
        <p class="chapter-image-caption">🎓 Профессор хорошего настроения 🎓</p>
    </div>
    """ if len(processed_images) > 5 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('funny_wisdom', 'Философия смеха!'))}
    </div>
</div>

<div id="chapter-social_butterfly" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 7</h3>
    <h2 class="chapter-main-title">Душа компании</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[6]}" alt="Photo for Chapter 7" class="chapter-image">
        <p class="chapter-image-caption">🎊 Генератор веселья в действии 🎊</p>
    </div>
    """ if len(processed_images) > 6 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('social_butterfly', 'Там где он - там веселье!'))}
    </div>
</div>

<div id="chapter-creative_chaos" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 8</h3>
    <h2 class="chapter-main-title">Творческий хаос</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[7]}" alt="Photo for Chapter 8" class="chapter-image">
        <p class="chapter-image-caption">🌈 Художник жизни 🌈</p>
    </div>
    """ if len(processed_images) > 7 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('creative_chaos', 'Креативность без границ!'))}
    </div>
</div>

<div id="chapter-finale_applause" class="book-page chapter-page">
    <h3 class="chapter-subtitle">Глава 9</h3>
    <h2 class="chapter-main-title">Финальные аплодисменты</h2>
    
    {f"""
    <div class="chapter-image-container">
        <img src="{processed_images[8]}" alt="Photo for Chapter 9" class="chapter-image">
        <p class="chapter-image-caption">🎭 До новых встреч, друзья! 🎭</p>
    </div>
    """ if len(processed_images) > 8 else ""}

    <div class="chapter-body">
        {format_paragraphs(chapters.get('finale_applause', 'Спасибо за веселье!'))}
    </div>
</div>

<!-- Final Page -->
<div class="book-page final-page">
    <div class="final-content">
        <p>
            Вот и подошла к концу наша весёлая история о <span class="humor-accent">{full_name}</span>.
        </p>
        <div class="final-ornament">🎉</div>
        <p>
            Спасибо за смех, позитив и вдохновение! <span class="humor-emoji">😊</span>
        </p>
        <div class="final-signature">
            Создано с улыбкой в Mythic<br>
            <em>"Смех делает мир ярче"</em>
        </div>
    </div>
</div>

</body>
</html>"""
    
    return html

def generate_standup_humor_book(run_id: str, images, comments, user_id=None):
    """Генерирует угарную стендап-книгу с дерзкими промптами и стилем standup_comedy"""
    print("🔥 Создание стендап-книги (дерзкий юмор)...")
    from app.services.llm_client import generate_memoir_chapter, strip_cliches
    from app.services.book_builder import analyze_profile_data, format_chapter_text
    from pathlib import Path
    import json
    run_dir = Path("data") / run_id
    posts_json = run_dir / "posts.json"
    images_dir = run_dir / "images"
    if posts_json.exists():
        posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
    else:
        posts_data = []
    analysis = analyze_profile_for_humor(posts_data)
    full_name = analysis.get("full_name", analysis.get("username", "Комик"))
    username = analysis.get("username", "comedian")
    actual_images = []
    if images_dir.exists():
        for img_file in sorted(images_dir.glob("*")):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                actual_images.append(img_file)
    standup_configs = [
        {'key': 'meeting', 'title': 'Пролог: Первая встреча', 'prompt': f"""Ты стендап-комик. Начни дерзко и коротко: 'Дамы и господа, знакомьтесь: {full_name}. Это не имя — это push-уведомление о том, что сейчас будет шумно.' Добавь: 'У каждого из нас есть знакомый-экскаватор: роет тему даже там, где уже асфальт. Вот {full_name} — тот самый.' Используй короткие, хлёсткие фразы, панчи, обращение к залу. НИКОГДА не пиши романтично!"""},
        {'key': 'first_impression', 'title': 'Глава первая: Первое впечатление', 'prompt': f"""Начни: 'Я захожу на тусовку, вижу {full_name} — и сразу вопрос: почему человек светится ярче, чем лампа эконом-класса?' Добавь: 'У {analysis.get("pronoun", "неё")} на лице та самая улыбка «— знаешь секрет? — какой? — не скажу!»' Используй современные сравнения (Wi-Fi, TikTok, Dolby Atmos), абсурдные ситуации. Пиши как стендап-комик на сцене. НИКОГДА не пиши романтично!"""},
        {'key': 'world_view', 'title': 'Глава вторая: Мир глазами комика', 'prompt': f"""Начни: 'У обычных людей дождь — это «влажно, зонт, спасибо». У {full_name} дождь — это когда небо чихает, потому что на земле жарят шашлык без разрешения.' Добавь диалоги с природой, абсурдные наблюдения. Используй: 'Ветер? Нам он портит причёску, {full_name} — настроение.' Пиши дерзко, с панчами. НИКОГДА не пиши романтично!"""},
        {'key': 'memorable_moments', 'title': 'Глава третья: Самые смешные моменты', 'prompt': f"""Начни: 'Попытка {full_name} купить хлеб превращается в шоу:' Добавь абсурдные диалоги типа: '— Дайте батон. — Режем? — Нет, я хочу, чтобы он страдал целиком!' Используй современные отсылки (YouTube, HR, Ньютон), неожиданные повороты. Пиши как стендап-комик. НИКОГДА не пиши романтично!"""},
        {'key': 'energy', 'title': 'Глава четвертая: Энергия и харизма', 'prompt': f"""Начни: 'Харизма {full_name}, ребята, — как вай-фай метро: не знаешь, кто настроил, но ловишь даже в туннеле.' Добавь: '{analysis.get("pronoun", "Она").title()} заходит в комнату, и лампочки такие: «Мы погорели, но держимся».' Используй современные сравнения (батарея телефона, самооценка), абсурдные ситуации. НИКОГДА не пиши романтично!"""},
        {'key': 'beauty_style', 'title': 'Глава пятая: Стиль и мода', 'prompt': f"""Начни: 'Пальто в цвет обоев из бабушкиной кухни? Есть. Кроссовки, будто ими уже сбежали из четырёх реальностей? Тоже.' Добавь: 'И ты такой: это провал моды или экзамен на широту души?' Используй абсурдные сравнения, современные отсылки, дерзкие вопросы. НИКОГДА не пиши романтично!"""},
        {'key': 'mystery', 'title': 'Глава шестая: Загадка личности', 'prompt': f"""Начни с вопросов: 'Почему {analysis.get("pronoun", "она")} опаздывает? Где теряются {analysis.get("pronoun_genitive", "её")} ключи? Чего {analysis.get("pronoun", "она")} не покажет в сторис?' Добавь абсурдные ответы типа: 'Там, где слоны боятся йоги времени, {full_name} ещё прикручивает люстру вдохновения.' Используй современные отсылки (параллельные вселенные, суперсилы). НИКОГДА не пиши романтично!"""},
        {'key': 'influence_on_me', 'title': 'Глава седьмая: Влияние на друзей', 'prompt': f"""Начни: 'После двух кофе с {full_name} друзья начинают разговаривать с микроволновкой:' Добавь абсурдные диалоги: '— Как думаешь, стоит ли менять работу? Динь! — «Подогрев завершён» — Вот видишь, знак!' Используй современные отсылки (солнечные очки ночью, идеи 24/7). НИКОГДА не пиши романтично!"""},
        {'key': 'observations', 'title': 'Глава восьмая: Наблюдения за жизнью', 'prompt': f"""Начни: 'Чтобы не чинить кран, надо… завести бассейн и мыть посуду там. Экология и спа-процедуры, две в одной!' Добавь лайфхаки типа: 'Опоздал? Скажи, что спас кота из горящего Excel-файла — и никто не станет уточнять.' Используй абсурдные советы, современные отсылки. НИКОГДА не пиши романтично!"""},
        {'key': 'funny_final', 'title': 'Глава девятая: Финальный аккорд', 'prompt': f"""Начни: 'Стоит пробке задохнуться, как появляется {full_name}, в плаще «LOL».' Добавь: '— Эй, седан на третьей полосе, перестань играть в тетрис, машины — не фигурки!' Используй современные отсылки (навигатор, анекдоты), абсурдные ситуации. НИКОГДА не пиши романтично!"""},
        {'key': 'gratitude_wishes', 'title': 'Эпилог: Благодарность и пожелания', 'prompt': f"""Начни: 'Ребята, вы — как TikTok: пролистываюсь, но хочется ещё.' Добавь: 'Не забудьте лайкнуть жизнь: ставьте сердечко утрам, подписывайтесь на удачу днём и делитесь мемами перед сном.' Используй современные отсылки, дерзкие пожелания. Заверши: 'Улыбайтесь бесплатнее, живите громче — и да пребудет с вами вай-фай харизмы {full_name}!' НИКОГДА не пиши романтично!"""},
    ]
    chapters = {}
    for config in standup_configs:
        for _ in range(3):
            try:
                generated_content = generate_memoir_chapter(
                    "humor_chapter",
                    {
                        'prompt': config['prompt'],
                        'style': 'standup_comedy',
                        'system_prompt': SYSTEM_STANDUP
                    },
                    temperature=0.55,
                    max_tokens=600
                )
                if not generated_content or len(generated_content.strip()) < 100:
                    continue
                if not ROMANTIC_WORDS.search(generated_content):
                    clean_content = strip_cliches(generated_content)
                    chapters[config['key']] = clean_content
                    break
            except Exception as e:
                print(f"❌ Ошибка генерации главы '{config['title']}': {e}")
        else:
            chapters[config['key']] = f"{config['title']} о {full_name} — настолько смешной, что даже GPT не справился! Зато мы попробовали!"
    html = create_humor_html(analysis, chapters, actual_images)
    html_file = run_dir / "book.html"
    html_file.write_text(html, encoding="utf-8")
    print("🔥 Стендап-книга создана!")
    return html

def build_book(run_id: str, images, comments, book_format: str = 'classic', user_id: str = None):
    """Создаёт полноценную юмористическую книгу с собственными промптами и дизайном"""
    print("🤣 Создание юмористической книги...")
    
    # Загружаем данные профиля
    run_dir = Path("data") / run_id
    posts_json = run_dir / "posts.json"
    images_dir = run_dir / "images"
    
    if posts_json.exists():
        posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
    else:
        posts_data = []
    
    # Анализируем профиль для юмора
    analysis = analyze_profile_for_humor(posts_data)
    
    # Собираем изображения
    actual_images = []
    if images_dir.exists():
        for img_file in sorted(images_dir.glob("*")):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                actual_images.append(img_file)
    
    # Генерируем контент в зависимости от формата
    # Классический формат
    chapters = generate_humor_chapters(analysis, actual_images)
    html = create_humor_html(analysis, chapters, actual_images)
    
    # Сохраняем
    html_file = run_dir / "book.html"
    html_file.write_text(html, encoding="utf-8")
    
    print("😄 Юмористическая книга создана!") 