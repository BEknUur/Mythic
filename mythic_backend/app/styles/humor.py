from pathlib import Path
import json
import random
import time
from app.services.llm_client import generate_memoir_chapter, strip_cliches, analyze_photo_for_memoir
from app.services.book_builder import analyze_profile_data, format_chapter_text

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
    
    # Анализируем для юмористического контекста
    analysis["comedian_name"] = analysis["full_name"] or analysis["username"]
    analysis["stage_name"] = f"@{analysis['username']}"
    
    return analysis

def generate_humor_chapters(analysis: dict, images: list[Path]) -> dict:
    """Генерирует главы юмористической книги"""
    
    full_name = analysis.get("full_name", analysis.get("username", "Комик"))
    username = analysis.get("username", "comedian")
    bio = analysis.get("bio", "")
    
    # Юмористическая конфигурация глав
    humor_configs = [
        {
            'key': 'introduction',
            'title': 'Знакомство с комиком',
            'prompt': f"""Напиши юмористическую главу "Знакомство с комиком" о {full_name} (5-6 абзацев).
            
            НАЧНИ: "Дорогие читатели, позвольте представить вам {full_name} - человека, который может рассмешить даже налогового инспектора!"
            
            СТРУКТУРА:
            1. Абзац: Представление комика с юмором
            2. Абзац: Первое впечатление - как он выглядит со стороны
            3. Абзац: Особенности характера с иронией
            4. Абзац: Как он относится к жизни - с юмором
            5. Абзац: Почему его стоит знать
            6. Абзац: Обещание веселого рассказа
            
            СТИЛЬ: Легкий юмор, ироничные замечания, разговорный стиль, без пошлости."""
        },
        {
            'key': 'daily_comedy',
            'title': 'Комедия повседневности',
            'prompt': f"""Напиши юмористическую главу "Комедия повседневности" о {full_name} (5-6 абзацев).
            
            НАЧНИ: "Обычный день {full_name} похож на серию комедийных скетчей..."
            
            СТРУКТУРА:
            1. Абзац: Как проходит обычный день
            2. Абзац: Забавные привычки и особенности
            3. Абзац: Как он общается с людьми
            4. Абзац: Неожиданные ситуации в его жизни
            5. Абзац: Как он превращает проблемы в анекдоты
            6. Абзац: Философия жизни с юмором
            
            СТИЛЬ: Наблюдательный юмор, забавные детали, позитивный взгляд."""
        },
        {
            'key': 'social_media_star',
            'title': 'Звезда соцсетей',
            'prompt': f"""Напиши юмористическую главу "Звезда соцсетей" о {full_name} и его присутствии в Instagram (5-6 абзацев).
            
            НАЧНИ: "Instagram @{username} - это место, где скучать не приходится никому!"
            
            СТРУКТУРА:
            1. Абзац: Как он ведет свой Instagram
            2. Абзац: Забавные подписи к фото
            3. Абзац: Реакции подписчиков
            4. Абзац: Как он выбирает что постить
            5. Абзац: Неожиданные моменты в постах
            6. Абзац: Почему за ним интересно следить
            
            СТИЛЬ: Современный юмор, интернет-культура, легкие шутки."""
        },
        {
            'key': 'photo_adventures',
            'title': 'Фотоприключения',
            'prompt': f"""Напиши юмористическую главу "Фотоприключения" о том, как {full_name} фотографируется (5-6 абзацев).
            
            НАЧНИ: "Когда {full_name} берет в руки камеру, начинается настоящее шоу!"
            
            СТРУКТУРА:
            1. Абзац: Как он готовится к фотосессии
            2. Абзац: Забавные позы и выражения лица
            3. Абзац: Неожиданные кадры и казусы
            4. Абзац: Как он выбирает лучшие фото
            5. Абзац: Реакция окружающих на процесс
            6. Абзац: Результат - фото с характером
            
            СТИЛЬ: Визуальный юмор, описания забавных ситуаций."""
        },
        {
            'key': 'unique_style',
            'title': 'Неповторимый стиль',
            'prompt': f"""Напиши юмористическую главу "Неповторимый стиль" о внешности и стиле {full_name} (5-6 абзацев).
            
            НАЧНИ: "Стиль {full_name} - это как хорошая шутка: запоминается с первого взгляда!"
            
            СТРУКТУРА:
            1. Абзац: Особенности внешности с юмором
            2. Абзац: Как он одевается
            3. Абзац: Его отношение к моде
            4. Абзац: Забавные детали образа
            5. Абзац: Как окружающие реагируют
            6. Абзац: Почему его стиль работает
            
            СТИЛЬ: Добрый юмор, без злых шуток, позитивное восприятие."""
        },
        {
            'key': 'funny_wisdom',
            'title': 'Мудрость с юмором',
            'prompt': f"""Напиши юмористическую главу "Мудрость с юмором" о жизненной философии {full_name} (5-6 абзацев).
            
            НАЧНИ: "Жизненная мудрость {full_name} похожа на хороший анекдот - в ней есть и смысл, и смех!"
            
            СТРУКТУРА:
            1. Абзац: Как он смотрит на жизнь
            2. Абзац: Забавные жизненные принципы
            3. Абзац: Как он решает проблемы
            4. Абзац: Его советы друзьям
            5. Абзац: Философия счастья
            6. Абзац: Почему с ним легко и весело
            
            СТИЛЬ: Философский юмор, жизненные наблюдения."""
        },
        {
            'key': 'social_butterfly',
            'title': 'Душа компании',
            'prompt': f"""Напиши юмористическую главу "Душа компании" о том, как {full_name} общается с людьми (5-6 абзацев).
            
            НАЧНИ: "Там, где появляется {full_name}, сразу становится веселее!"
            
            СТРУКТУРА:
            1. Абзац: Как он ведет себя в компании
            2. Абзац: Его способность поднимать настроение
            3. Абзац: Забавные истории с друзьями
            4. Абзац: Как он знакомится с новыми людьми
            5. Абзац: Его талант к импровизации
            6. Абзац: Почему люди к нему тянутся
            
            СТИЛЬ: Социальный юмор, истории о дружбе."""
        },
        {
            'key': 'creative_chaos',
            'title': 'Творческий хаос',
            'prompt': f"""Напиши юмористическую главу "Творческий хаос" о креативности {full_name} (5-6 абзацев).
            
            НАЧНИ: "Креативность {full_name} - это как ураган в художественной мастерской!"
            
            СТРУКТУРА:
            1. Абзац: Как рождаются его идеи
            2. Абзац: Процесс творчества
            3. Абзац: Неожиданные результаты
            4. Абзац: Как он вдохновляется
            5. Абзац: Творческие эксперименты
            6. Абзац: Почему хаос - это хорошо
            
            СТИЛЬ: Креативный юмор, описания процесса."""
        },
        {
            'key': 'finale_applause',
            'title': 'Финальные аплодисменты',
            'prompt': f"""Напиши юмористическую финальную главу "Финальные аплодисменты" о {full_name} (6-7 абзацев).
            
            НАЧНИ: "Вот и подошла к концу наша веселая история о {full_name}..."
            
            СТРУКТУРА:
            1. Абзац: Подведение итогов с юмором
            2. Абзац: Что мы узнали о герое
            3. Абзац: Его влияние на окружающих
            4. Абзац: Пожелания на будущее
            5. Абзац: Благодарность за позитив
            6. Абзац: Призыв не терять чувство юмора
            7. Абзац: Веселое прощание
            
            СТИЛЬ: Теплый финал, благодарность, позитивные пожелания."""
        }
    ]
    
    chapters = {}
    
    for config in humor_configs:
        try:
            print(f"😄 Генерирую главу '{config['title']}'...")
            
            generated_content = generate_memoir_chapter("humor_chapter", {
                'prompt': config['prompt'],
                'style': 'humorous_light'
            })
            
            if len(generated_content.strip()) < 100:
                chapters[config['key']] = f"В этой главе мы узнаем о {config['title'].lower()} нашего героя {full_name}. Смех и позитив гарантированы!"
            else:
                clean_content = strip_cliches(generated_content)
                chapters[config['key']] = format_chapter_text(clean_content)
                
        except Exception as e:
            print(f"❌ Ошибка генерации главы '{config['title']}': {e}")
            chapters[config['key']] = f"Глава о {config['title'].lower()} полна смеха и позитива."
    
    return chapters

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
    <link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;400;700&family=Nunito:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    
    <style>
    :root {{
        --sunshine: #ffd54f;
        --orange: #ff7043;
        --pink: #ec407a;
        --purple: #ab47bc;
        --blue: #42a5f5;
        --green: #66bb6a;
        --text: #37474f;
        --light-bg: #fffde7;
        --card-bg: #fff9c4;
        --shadow: rgba(255, 193, 7, 0.3);
    }}
    
    body {{
        font-family: 'Nunito', sans-serif;
        background: linear-gradient(135deg, var(--light-bg) 0%, var(--card-bg) 100%);
        color: var(--text);
        line-height: 1.6;
        font-size: 16px;
        margin: 0;
        padding: 0;
        max-width: 900px;
        margin: 0 auto;
    }}
    
    .humor-page {{
        min-height: 95vh;
        padding: 2.5cm;
        background: white;
        box-shadow: 0 8px 40px var(--shadow);
        margin: 20px auto;
        border-radius: 20px;
        border: 4px solid var(--sunshine);
        position: relative;
        overflow: hidden;
    }}
    
    .humor-page::before {{
        content: '😄';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 2rem;
        opacity: 0.3;
        animation: bounce 2s infinite;
    }}
    
    @keyframes bounce {{
        0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
        40% {{ transform: translateY(-10px); }}
        60% {{ transform: translateY(-5px); }}
    }}
    
    .cover-humor {{
        text-align: center;
        padding: 4cm 2cm;
        background: linear-gradient(135deg, var(--sunshine) 0%, var(--orange) 50%, var(--pink) 100%);
        color: white;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
    }}
    
    .cover-humor::before {{
        content: '🎭🎪🎨🎯🎲';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        font-size: 4rem;
        opacity: 0.1;
        letter-spacing: 2rem;
        animation: slide 10s infinite linear;
    }}
    
    @keyframes slide {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    
    .cover-title {{
        font-family: 'Comfortaa', cursive;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }}
    
    .cover-subtitle {{
        font-family: 'Comfortaa', cursive;
        font-size: 1.4rem;
        margin-bottom: 2rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }}
    
    .cover-epigraph {{
        font-style: italic;
        border: 3px solid white;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 500px;
        border-radius: 15px;
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 1;
    }}
    
    .chapter-header {{
        margin-bottom: 3rem;
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, var(--sunshine) 0%, var(--orange) 100%);
        border-radius: 15px;
        color: white;
        position: relative;
    }}
    
    .chapter-number {{
        font-family: 'Comfortaa', cursive;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
    }}
    
    .chapter-title {{
        font-family: 'Comfortaa', cursive;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    
    .humor-text {{
        text-align: justify;
        line-height: 1.8;
        font-size: 17px;
        margin-bottom: 1.5em;
        padding: 1.5rem;
        background: var(--card-bg);
        border-radius: 15px;
        border-left: 5px solid var(--sunshine);
        position: relative;
    }}
    
    .humor-text::before {{
        content: '😊';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 1.5rem;
        opacity: 0.3;
    }}
    
    .humor-photo {{
        margin: 3rem 0;
        text-align: center;
        position: relative;
    }}
    
    .photo-frame {{
        display: inline-block;
        padding: 20px;
        background: linear-gradient(135deg, var(--pink) 0%, var(--purple) 50%, var(--blue) 100%);
        border-radius: 20px;
        box-shadow: 0 10px 30px var(--shadow);
        transform: rotate(-2deg);
        transition: transform 0.3s ease;
    }}
    
    .photo-frame:hover {{
        transform: rotate(0deg) scale(1.05);
    }}
    
    .photo-frame img {{
        max-width: 100%;
        max-height: 350px;
        border-radius: 15px;
        border: 3px solid white;
    }}
    
    .photo-caption {{
        font-family: 'Comfortaa', cursive;
        font-size: 1.1rem;
        color: var(--text);
        margin-top: 1.5rem;
        text-align: center;
        font-weight: 600;
        background: var(--card-bg);
        padding: 1rem;
        border-radius: 10px;
        display: inline-block;
    }}
    
    .humor-finale {{
        text-align: center;
        margin-top: 4rem;
        padding: 3rem;
        background: linear-gradient(135deg, var(--green) 0%, var(--blue) 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 10px 30px var(--shadow);
    }}
    
    .humor-signature {{
        font-family: 'Comfortaa', cursive;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 2rem;
    }}
    
    .toc-humor {{
        background: var(--card-bg);
        border: 3px solid var(--sunshine);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        position: relative;
    }}
    
    .toc-humor::before {{
        content: '📚';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 2rem;
        opacity: 0.3;
    }}
    
    .toc-title {{
        font-family: 'Comfortaa', cursive;
        font-size: 2.2rem;
        color: var(--text);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }}
    
    .toc-item {{
        margin-bottom: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }}
    
    .toc-item:hover {{
        transform: translateX(5px);
    }}
    
    .toc-chapter {{
        font-weight: 600;
        color: var(--text);
        font-size: 1.1rem;
    }}
    
    .toc-page {{
        background: var(--sunshine);
        color: var(--text);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-family: 'Comfortaa', cursive;
        font-weight: 700;
    }}
    
    .emoji-decoration {{
        font-size: 1.5rem;
        margin: 0 0.5rem;
    }}
    
    @media (max-width: 768px) {{
        .humor-page {{
            padding: 2cm 1.5cm;
            margin: 10px;
        }}
        
        .cover-title {{
            font-size: 2.5rem;
        }}
        
        .chapter-title {{
            font-size: 1.8rem;
        }}
    }}
    </style>
</head>
<body>

<!-- ОБЛОЖКА ЮМОРА -->
<div class="humor-page cover-humor">
    <h1 class="cover-title">{book_title} 😄</h1>
    <p class="cover-subtitle">Юмористическая летопись</p>
    
    <div class="cover-epigraph">
        Смех - это лучшее лекарство,<br>
        а {full_name} - лучший доктор!<br><br>
        <strong>Готовьтесь к позитивной терапии! 🎭</strong>
    </div>
    
    <div style="margin-top: 3rem; font-size: 1.2rem; position: relative; z-index: 1;">
        <strong>Комедийная биография @{username}</strong><br>
        <em>Написано с улыбкой и хорошим настроением</em>
    </div>
</div>

<!-- ОГЛАВЛЕНИЕ -->
<div class="humor-page">
    <div class="toc-humor">
        <h2 class="toc-title">📖 Что нас ждет впереди 📖</h2>
        
        <div class="toc-item">
            <span class="toc-chapter">😊 Знакомство с комиком</span>
            <span class="toc-page">3</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">🎭 Комедия повседневности</span>
            <span class="toc-page">4</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">📱 Звезда соцсетей</span>
            <span class="toc-page">5</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">📸 Фотоприключения</span>
            <span class="toc-page">6</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">👗 Неповторимый стиль</span>
            <span class="toc-page">7</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">🧠 Мудрость с юмором</span>
            <span class="toc-page">8</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">🎉 Душа компании</span>
            <span class="toc-page">9</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">🎨 Творческий хаос</span>
            <span class="toc-page">10</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">👏 Финальные аплодисменты</span>
            <span class="toc-page">11</span>
        </div>
    </div>
</div>

<!-- ГЛАВЫ ЮМОРА -->
<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 1</div>
        <h2 class="chapter-title">😊 Знакомство с комиком</h2>
    </div>
    <div class="humor-text">{chapters.get('introduction', 'Знакомьтесь - наш главный герой!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Наш герой"></div><div class="photo-caption">🌟 Вот он - источник позитива! 🌟</div></div>' if processed_images else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 2</div>
        <h2 class="chapter-title">🎭 Комедия повседневности</h2>
    </div>
    <div class="humor-text">{chapters.get('daily_comedy', 'Каждый день - новая комедия!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Повседневная жизнь"></div><div class="photo-caption">😄 Обычный день необычного человека 😄</div></div>' if len(processed_images) > 1 else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 3</div>
        <h2 class="chapter-title">📱 Звезда соцсетей</h2>
    </div>
    <div class="humor-text">{chapters.get('social_media_star', 'Instagram как источник веселья!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[2]}" alt="Звезда соцсетей"></div><div class="photo-caption">📸 Мастер селфи и позитива 📸</div></div>' if len(processed_images) > 2 else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 4</div>
        <h2 class="chapter-title">📸 Фотоприключения</h2>
    </div>
    <div class="humor-text">{chapters.get('photo_adventures', 'Каждое фото - приключение!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[3]}" alt="Фотоприключения"></div><div class="photo-caption">🎪 Цирк в одном кадре 🎪</div></div>' if len(processed_images) > 3 else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 5</div>
        <h2 class="chapter-title">👗 Неповторимый стиль</h2>
    </div>
    <div class="humor-text">{chapters.get('unique_style', 'Стиль - это состояние души!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[4]}" alt="Неповторимый стиль"></div><div class="photo-caption">✨ Икона стиля и хорошего настроения ✨</div></div>' if len(processed_images) > 4 else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 6</div>
        <h2 class="chapter-title">🧠 Мудрость с юмором</h2>
    </div>
    <div class="humor-text">{chapters.get('funny_wisdom', 'Философия смеха!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[5]}" alt="Мудрость с юмором"></div><div class="photo-caption">🎓 Профессор хорошего настроения 🎓</div></div>' if len(processed_images) > 5 else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 7</div>
        <h2 class="chapter-title">🎉 Душа компании</h2>
    </div>
    <div class="humor-text">{chapters.get('social_butterfly', 'Там где он - там веселье!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[6]}" alt="Душа компании"></div><div class="photo-caption">🎊 Генератор веселья в действии 🎊</div></div>' if len(processed_images) > 6 else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 8</div>
        <h2 class="chapter-title">🎨 Творческий хаос</h2>
    </div>
    <div class="humor-text">{chapters.get('creative_chaos', 'Креативность без границ!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[7]}" alt="Творческий хаос"></div><div class="photo-caption">🌈 Художник жизни 🌈</div></div>' if len(processed_images) > 7 else ''}
</div>

<div class="humor-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава 9</div>
        <h2 class="chapter-title">👏 Финальные аплодисменты</h2>
    </div>
    <div class="humor-text">{chapters.get('finale_applause', 'Спасибо за веселье!')}</div>
    {f'<div class="humor-photo"><div class="photo-frame"><img src="{processed_images[8]}" alt="Финал"></div><div class="photo-caption">🎭 До новых встреч, друзья! 🎭</div></div>' if len(processed_images) > 8 else ''}
    
    <div class="humor-finale">
        <div style="font-size: 2rem; margin-bottom: 2rem;">
            🎉 Конец первой части веселых историй 🎉
        </div>
        
        <div class="humor-signature">
            Спасибо {full_name} за позитив и вдохновение!<br>
            <em>Продолжение следует... 😉</em>
        </div>
        
        <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
            Создано с улыбкой в Mythic • "Смех делает мир ярче" 🌟
        </div>
    </div>
</div>

</body>
</html>"""
    
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
    
    # Генерируем юмористические главы
    chapters = generate_humor_chapters(analysis, actual_images)
    
    # Создаем HTML
    html = create_humor_html(analysis, chapters, actual_images)
    
    # Сохраняем
    html_file = run_dir / "book.html"
    html_file.write_text(html, encoding="utf-8")
    
    print("😄 Юмористическая книга создана!") 