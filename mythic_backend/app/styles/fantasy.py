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
    """Генерирует главы фэнтези-книги"""
    
    full_name = analysis.get("full_name", analysis.get("username", "Герой"))
    username = analysis.get("username", "hero")
    bio = analysis.get("bio", "")
    
    # Фэнтези конфигурация глав
    fantasy_configs = [
        {
            'key': 'prophecy',
            'title': 'Древнее пророчество',
            'prompt': f"""Напиши главу "Древнее пророчество" о герое по имени {full_name} в жанре эпического фэнтези (5-6 абзацев).
            
            НАЧНИ: "В древних свитках Академии Магов было записано пророчество о герое, чье имя станет легендой..."
            
            СТРУКТУРА:
            1. Абзац: Древнее пророчество в магических свитках
            2. Абзац: Описание героя {full_name} - благородные черты, магическая аура
            3. Абзац: Знаки судьбы в его облике и характере
            4. Абзац: Особая сила, что дремлет в его душе
            5. Абзац: Предназначение изменить мир
            6. Абзац: Начало великого пути
            
            СТИЛЬ: Эпическое фэнтези, архаичный язык, магические метафоры, описания ауры и силы."""
        },
        {
            'key': 'magical_realm',
            'title': 'Магическое королевство',
            'prompt': f"""Напиши главу "Магическое королевство" о мире героя {full_name} в жанре фэнтези (5-6 абзацев).
            
            НАЧНИ: "Королевство @{username} раскинулось между мирами, где магия течет в каждом камне..."
            
            СТРУКТУРА:
            1. Абзац: Описание магического королевства
            2. Абзац: Особенности этого мира - кристаллы, руны, древние артефакты
            3. Абзац: Жители королевства и их способности
            4. Абзац: Природа пропитана магией
            5. Абзац: Герой как хранитель этого мира
            6. Абзац: Гармония между магией и природой
            
            СТИЛЬ: Детальные описания магического мира, мистические элементы."""
        },
        {
            'key': 'ancient_wisdom',
            'title': 'Древняя мудрость',
            'prompt': f"""Напиши главу "Древняя мудрость" о знаниях героя {full_name} в жанре фэнтези (5-6 абзацев).
            
            НАЧНИ: "В глазах {full_name} читается мудрость веков, словно он помнит времена Первой Магии..."
            
            СТРУКТУРА:
            1. Абзац: Древняя мудрость в глазах героя
            2. Абзац: Знание тайных рун и заклинаний
            3. Абзац: Понимание языка природы и стихий
            4. Абзац: Связь с духами предков
            5. Абзац: Дар предвидения будущего
            6. Абзац: Ответственность за древние знания
            
            СТИЛЬ: Мистический, философский, с элементами древних знаний."""
        },
        {
            'key': 'magical_artifacts',
            'title': 'Магические артефакты',
            'prompt': f"""Напиши главу "Магические артефакты" о сокровищах героя {full_name} в жанре фэнтези (5-6 абзацев).
            
            НАЧНИ: "Каждый предмет в коллекции {full_name} излучает древнюю магию..."
            
            СТРУКТУРА:
            1. Абзац: Коллекция магических артефактов
            2. Абзац: Кристаллы силы и их свойства
            3. Абзац: Древние амулеты защиты
            4. Абзац: Руны памяти и мудрости
            5. Абзац: Связь артефактов с душой героя
            6. Абзац: Сила, что растет с каждым днем
            
            СТИЛЬ: Описания магических предметов, их силы и назначения."""
        },
        {
            'key': 'elemental_power',
            'title': 'Власть над стихиями',
            'prompt': f"""Напиши главу "Власть над стихиями" о магических способностях {full_name} в жанре фэнтези (5-6 абзацев).
            
            НАЧНИ: "Стихии повинуются {full_name} как древнему повелителю..."
            
            СТРУКТУРА:
            1. Абзац: Власть над четырьмя стихиями
            2. Абзац: Огонь - страсть и сила воли
            3. Абзац: Вода - мудрость и исцеление
            4. Абзац: Земля - стойкость и защита
            5. Абзац: Воздух - свобода и вдохновение
            6. Абзац: Гармония всех стихий в одном существе
            
            СТИЛЬ: Магические описания, власть над природными силами."""
        },
        {
            'key': 'dragon_bond',
            'title': 'Союз с драконом',
            'prompt': f"""Напиши главу "Союз с драконом" о магической связи {full_name} с древним драконом в жанре фэнтези (5-6 абзацев).
            
            НАЧНИ: "Древний дракон признал в {full_name} достойного союзника..."
            
            СТРУКТУРА:
            1. Абзац: Встреча с древним драконом
            2. Абзац: Взаимное признание и уважение
            3. Абзац: Магическая связь душ
            4. Абзац: Общие полеты над королевством
            5. Абзац: Дракон как хранитель и советник
            6. Абзац: Сила, что удваивается в союзе
            
            СТИЛЬ: Эпические описания, связь с мифическими существами."""
        },
        {
            'key': 'quest_calling',
            'title': 'Зов приключений',
            'prompt': f"""Напиши главу "Зов приключений" о судьбе героя {full_name} в жанре фэнтези (5-6 абзацев).
            
            НАЧНИ: "Судьба зовет {full_name} в великий поход..."
            
            СТРУКТУРА:
            1. Абзац: Зов судьбы и предназначения
            2. Абзац: Знаки, указывающие путь
            3. Абзац: Подготовка к великому походу
            4. Абзац: Спутники и союзники
            5. Абзац: Опасности, что ждут впереди
            6. Абзац: Решимость идти до конца
            
            СТИЛЬ: Героический, вдохновляющий, полный решимости."""
        },
        {
            'key': 'legendary_deeds',
            'title': 'Легендарные подвиги',
            'prompt': f"""Напиши главу "Легендарные подвиги" о великих делах {full_name} в жанре фэнтези (5-6 абзацев).
            
            НАЧНИ: "Барды по всему королевству слагают песни о подвигах {full_name}..."
            
            СТРУКТУРА:
            1. Абзац: Песни и легенды о герое
            2. Абзац: Спасение заколдованного леса
            3. Абзац: Победа над темными силами
            4. Абзац: Освобождение пленных душ
            5. Абзац: Восстановление древних святилищ
            6. Абзац: Слава, что переживет века
            
            СТИЛЬ: Эпические подвиги, героические деяния."""
        },
        {
            'key': 'eternal_legacy',
            'title': 'Вечное наследие',
            'prompt': f"""Напиши главу "Вечное наследие" о бессмертной славе {full_name} в жанре фэнтези (6-7 абзацев).
            
            НАЧНИ: "Имя {full_name} навсегда вписано в Книгу Героев..."
            
            СТРУКТУРА:
            1. Абзац: Имя в Книге Героев
            2. Абзац: Статуи и памятники в его честь
            3. Абзац: Ученики, продолжающие дело
            4. Абзац: Магия, что живет в его наследии
            5. Абзац: Вдохновение для будущих поколений
            6. Абзац: Благодарность всего королевства
            7. Абзац: Вечная память и почитание
            
            СТИЛЬ: Торжественный, вдохновляющий финал."""
        }
    ]
    
    chapters = {}
    
    for config in fantasy_configs:
        try:
            print(f"🧙‍♂️ Генерирую главу '{config['title']}'...")
            
            generated_content = generate_memoir_chapter("fantasy_chapter", {
                'prompt': config['prompt'],
                'style': 'epic_fantasy'
            })
            
            if len(generated_content.strip()) < 100:
                chapters[config['key']] = f"В этой главе рассказывается о {config['title'].lower()} героя {full_name}. Магия окружает каждый его шаг, а судьба ведет к великим свершениям."
            else:
                clean_content = strip_cliches(generated_content)
                chapters[config['key']] = format_chapter_text(clean_content)
                
        except Exception as e:
            print(f"❌ Ошибка генерации главы '{config['title']}': {e}")
            chapters[config['key']] = f"Глава о {config['title'].lower()} полна магии и древних тайн."
    
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
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    
    <style>
    :root {{
        --parchment: #f4f1e8;
        --dark-ink: #2c1810;
        --gold: #d4af37;
        --deep-purple: #4a148c;
        --mystic-blue: #1a237e;
        --shadow: rgba(74, 20, 140, 0.3);
        --ancient-bronze: #8b4513;
    }}
    
    body {{
        font-family: 'Crimson Text', serif;
        background: linear-gradient(135deg, var(--parchment) 0%, #e8e2d5 100%);
        color: var(--dark-ink);
        line-height: 1.7;
        font-size: 16px;
        margin: 0;
        padding: 0;
        max-width: 900px;
        margin: 0 auto;
    }}
    
    .fantasy-page {{
        min-height: 95vh;
        padding: 3cm 2.5cm;
        background: var(--parchment);
        box-shadow: 0 10px 50px var(--shadow);
        margin: 20px auto;
        border: 3px solid var(--gold);
        border-radius: 15px;
        position: relative;
    }}
    
    .fantasy-page::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="ancient" patternUnits="userSpaceOnUse" width="20" height="20"><circle cx="10" cy="10" r="1" fill="%23d4af37" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23ancient)"/></svg>');
        pointer-events: none;
        border-radius: 12px;
    }}
    
    .cover-fantasy {{
        text-align: center;
        padding: 4cm 2cm;
        background: linear-gradient(135deg, var(--deep-purple) 0%, var(--mystic-blue) 100%);
        color: var(--gold);
        border-radius: 15px;
        position: relative;
        overflow: hidden;
    }}
    
    .cover-fantasy::before {{
        content: '⚔️';
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 3rem;
        opacity: 0.3;
    }}
    
    .cover-title {{
        font-family: 'Cinzel', serif;
        font-size: 3.2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        letter-spacing: 2px;
    }}
    
    .cover-subtitle {{
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }}
    
    .cover-epigraph {{
        font-style: italic;
        border: 2px solid var(--gold);
        padding: 2rem;
        margin: 2rem auto;
        max-width: 500px;
        border-radius: 10px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }}
    
    .chapter-header {{
        margin-bottom: 3rem;
        text-align: center;
        border-bottom: 3px solid var(--gold);
        padding-bottom: 1.5rem;
    }}
    
    .chapter-number {{
        font-family: 'Cinzel', serif;
        font-size: 1rem;
        color: var(--deep-purple);
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 1rem;
    }}
    
    .chapter-title {{
        font-family: 'Cinzel', serif;
        font-size: 2.5rem;
        font-weight: 600;
        color: var(--deep-purple);
        margin: 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }}
    
    .fantasy-text {{
        text-align: justify;
        line-height: 1.8;
        font-size: 17px;
        text-indent: 2em;
        margin-bottom: 1.5em;
        position: relative;
        z-index: 1;
    }}
    
    .fantasy-text::first-letter {{
        font-family: 'Cinzel', serif;
        font-size: 4rem;
        font-weight: 700;
        color: var(--deep-purple);
        float: left;
        line-height: 1;
        margin: 0.1em 0.1em 0 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    
    .fantasy-photo {{
        margin: 3rem 0;
        text-align: center;
        position: relative;
    }}
    
    .photo-frame {{
        display: inline-block;
        padding: 20px;
        background: linear-gradient(135deg, var(--gold) 0%, var(--ancient-bronze) 100%);
        border-radius: 15px;
        box-shadow: 0 8px 30px var(--shadow);
        transform: rotate(-1deg);
        transition: transform 0.3s ease;
    }}
    
    .photo-frame:hover {{
        transform: rotate(0deg) scale(1.05);
    }}
    
    .photo-frame img {{
        max-width: 100%;
        max-height: 350px;
        border-radius: 10px;
        border: 2px solid var(--parchment);
    }}
    
    .photo-caption {{
        font-family: 'Cinzel', serif;
        font-style: italic;
        font-size: 1rem;
        color: var(--deep-purple);
        margin-top: 1.5rem;
        text-align: center;
        font-weight: 600;
    }}
    
    .fantasy-finale {{
        text-align: center;
        margin-top: 4rem;
        padding: 3rem;
        background: linear-gradient(135deg, var(--gold) 0%, var(--ancient-bronze) 100%);
        border-radius: 15px;
        color: var(--parchment);
        box-shadow: 0 8px 30px var(--shadow);
    }}
    
    .fantasy-signature {{
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 2rem;
    }}
    
    .toc-fantasy {{
        background: linear-gradient(135deg, var(--parchment) 0%, #e8e2d5 100%);
        border: 2px solid var(--gold);
        border-radius: 15px;
        padding: 3rem;
        margin: 2rem 0;
    }}
    
    .toc-title {{
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        color: var(--deep-purple);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
    }}
    
    .toc-item {{
        margin-bottom: 1rem;
        padding: 0.8rem;
        border-bottom: 1px dotted var(--gold);
        display: flex;
        justify-content: space-between;
        font-size: 1.1rem;
    }}
    
    .toc-chapter {{
        font-weight: 600;
        color: var(--dark-ink);
    }}
    
    .toc-page {{
        color: var(--deep-purple);
        font-family: 'Cinzel', serif;
    }}
    
    @media (max-width: 768px) {{
        .fantasy-page {{
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
    </style>
</head>
<body>

<!-- ОБЛОЖКА ФЭНТЕЗИ -->
<div class="fantasy-page cover-fantasy">
    <h1 class="cover-title">{book_title}</h1>
    <p class="cover-subtitle">Эпическая сага о великом герое</p>
    
    <div class="cover-epigraph">
        В древних свитках написано:<br>
        "Придет герой, чье имя станет легендой,<br>
        и деяния его переживут века..."<br><br>
        <strong>Этот герой - {full_name}</strong>
    </div>
    
    <div style="margin-top: 3rem; font-size: 1.2rem;">
        <strong>Летопись героя @{username}</strong><br>
        <em>Написано магическими чернилами</em>
    </div>
</div>

<!-- ОГЛАВЛЕНИЕ -->
<div class="fantasy-page">
    <div class="toc-fantasy">
        <h2 class="toc-title">⚔️ Содержание Хроник ⚔️</h2>
        
        <div class="toc-item">
            <span class="toc-chapter">Древнее пророчество</span>
            <span class="toc-page">III</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Магическое королевство</span>
            <span class="toc-page">IV</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Древняя мудрость</span>
            <span class="toc-page">V</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Магические артефакты</span>
            <span class="toc-page">VI</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Власть над стихиями</span>
            <span class="toc-page">VII</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Союз с драконом</span>
            <span class="toc-page">VIII</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Зов приключений</span>
            <span class="toc-page">IX</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Легендарные подвиги</span>
            <span class="toc-page">X</span>
        </div>
        
        <div class="toc-item">
            <span class="toc-chapter">Вечное наследие</span>
            <span class="toc-page">XI</span>
        </div>
    </div>
</div>

<!-- ГЛАВЫ ФЭНТЕЗИ -->
<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава I</div>
        <h2 class="chapter-title">🔮 Древнее пророчество</h2>
    </div>
    <div class="fantasy-text">{chapters.get('prophecy', 'Древние пророчества говорят о великом герое...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[0]}" alt="Герой пророчества"></div><div class="photo-caption">✨ Избранный судьбой ✨</div></div>' if processed_images else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава II</div>
        <h2 class="chapter-title">🏰 Магическое королевство</h2>
    </div>
    <div class="fantasy-text">{chapters.get('magical_realm', 'Королевство магии раскинулось между мирами...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[1]}" alt="Владыка королевства"></div><div class="photo-caption">👑 Правитель магических земель 👑</div></div>' if len(processed_images) > 1 else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава III</div>
        <h2 class="chapter-title">📜 Древняя мудрость</h2>
    </div>
    <div class="fantasy-text">{chapters.get('ancient_wisdom', 'Мудрость веков живет в глазах героя...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[2]}" alt="Хранитель мудрости"></div><div class="photo-caption">🧙‍♂️ Носитель древних знаний 🧙‍♂️</div></div>' if len(processed_images) > 2 else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава IV</div>
        <h2 class="chapter-title">💎 Магические артефакты</h2>
    </div>
    <div class="fantasy-text">{chapters.get('magical_artifacts', 'Древние артефакты хранят силу веков...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[3]}" alt="Собиратель артефактов"></div><div class="photo-caption">⚡ Повелитель древних сил ⚡</div></div>' if len(processed_images) > 3 else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава V</div>
        <h2 class="chapter-title">🌪️ Власть над стихиями</h2>
    </div>
    <div class="fantasy-text">{chapters.get('elemental_power', 'Стихии повинуются воле героя...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[4]}" alt="Повелитель стихий"></div><div class="photo-caption">🔥💧🌍💨 Владыка четырех стихий 🔥💧🌍💨</div></div>' if len(processed_images) > 4 else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава VI</div>
        <h2 class="chapter-title">🐉 Союз с драконом</h2>
    </div>
    <div class="fantasy-text">{chapters.get('dragon_bond', 'Древний дракон признал в герое равного...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[5]}" alt="Друг драконов"></div><div class="photo-caption">🐲 Союзник древних драконов 🐲</div></div>' if len(processed_images) > 5 else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава VII</div>
        <h2 class="chapter-title">🗡️ Зов приключений</h2>
    </div>
    <div class="fantasy-text">{chapters.get('quest_calling', 'Судьба зовет героя в великий поход...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[6]}" alt="Искатель приключений"></div><div class="photo-caption">⚔️ Странник судьбы ⚔️</div></div>' if len(processed_images) > 6 else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава VIII</div>
        <h2 class="chapter-title">🏆 Легендарные подвиги</h2>
    </div>
    <div class="fantasy-text">{chapters.get('legendary_deeds', 'Барды слагают песни о подвигах героя...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[7]}" alt="Легендарный герой"></div><div class="photo-caption">🎵 Герой легенд и баллад 🎵</div></div>' if len(processed_images) > 7 else ''}
</div>

<div class="fantasy-page">
    <div class="chapter-header">
        <div class="chapter-number">Глава IX</div>
        <h2 class="chapter-title">👑 Вечное наследие</h2>
    </div>
    <div class="fantasy-text">{chapters.get('eternal_legacy', 'Имя героя навсегда вписано в историю...')}</div>
    {f'<div class="fantasy-photo"><div class="photo-frame"><img src="{processed_images[8]}" alt="Бессмертный герой"></div><div class="photo-caption">⭐ Вечная слава и почитание ⭐</div></div>' if len(processed_images) > 8 else ''}
    
    <div class="fantasy-finale">
        <div style="font-size: 1.6rem; margin-bottom: 2rem;">
            ⚔️ Конец первой книги хроник ⚔️
        </div>
        
        <div class="fantasy-signature">
            Летопись героя {full_name} будет продолжена...<br>
            <em>Написано в Академии Магических Искусств</em>
        </div>
        
        <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
            Создано магией Mythic • "Каждый достоин стать героем легенд"
        </div>
    </div>
</div>

</body>
</html>"""
    
    return html



def build_fantasy_book(run_id, images, comments, book_format='classic', user_id=None):
    return _build_fantasy_book(run_id, images, comments, book_format, user_id) 