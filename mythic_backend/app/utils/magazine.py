from __future__ import annotations
from pathlib import Path
import json
import random

def wrap_html_in_magazine(body_html: str, analysis: dict, style: str = "romantic") -> str:
    """Оборачивает сгенерированный body_html в журнальный макет (A4, двухколонки, обложка).
    Не делает сложной структуры оглавления – просто добавляет обложку + css.
    """
    title = analysis.get("full_name") or analysis.get("username", "Mythic AI")
    subtitle = "Персональная история" if style == "romantic" else (
        "Путешествие сквозь магию" if style == "fantasy" else "Смех до слёз" )
    # базовые цвета
    palette = {
        "romantic": "#e84393",
        "fantasy":  "#6c5ce7",
        "humor":    "#fdcb6e"
    }.get(style, "#e84393")
    
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Журнал</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fafafa;
            margin: 0;
            padding: 0;
        }}
        
        .magazine-cover {{
            page-break-after: always;
            height: 100vh;
            background: linear-gradient(135deg, {palette}22, {palette}44);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 2rem;
        }}
        
        .magazine-title {{
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            font-weight: 700;
            color: {palette};
            margin-bottom: 1rem;
        }}
        
        .magazine-subtitle {{
            font-size: 1.5rem;
            color: #666;
            margin-bottom: 2rem;
        }}
        
        .magazine-date {{
            font-size: 1rem;
            color: #999;
            position: absolute;
            bottom: 2rem;
        }}
        
        .magazine-content {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .magazine-content h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 2.5rem;
            color: {palette};
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .magazine-content h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            color: {palette};
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        
        .magazine-content p {{
            columns: 2;
            column-gap: 2rem;
            text-align: justify;
            margin-bottom: 1.5rem;
        }}
        
        .magazine-content p:first-letter {{
            font-size: 3rem;
            font-weight: bold;
            float: left;
            line-height: 1;
            margin-right: 0.5rem;
            margin-top: 0.2rem;
            color: {palette};
        }}
        
        .magazine-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1.5rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .page-number {{
            position: fixed;
            bottom: 1rem;
            right: 50%;
            transform: translateX(50%);
            font-size: 0.9rem;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="magazine-cover">
        <h1 class="magazine-title">{title}</h1>
        <p class="magazine-subtitle">{subtitle}</p>
        <div class="magazine-date">Создано с любовью • {Path().resolve().name}</div>
    </div>
    
    <div class="magazine-content">
        {body_html}
    </div>
    
    <div class="page-number">1</div>
</body>
</html>"""

def create_magazine_html(analysis: dict, images: list, style: str = "romantic") -> str:
    """Создает полноценный интерактивный журнал с эффектом переворота страниц"""
    
    # 1. Определяем палитру и контент
    palette = {
        "romantic": {"primary": "#d63384", "secondary": "#fd7e14", "accent": "#ffc107", "bg": "#fff5f5"},
        "fantasy": {"primary": "#6f42c1", "secondary": "#e83e8c", "accent": "#fd7e14", "bg": "#f8f7ff"},
        "humor": {"primary": "#fd7e14", "secondary": "#20c997", "accent": "#e83e8c", "bg": "#fffbf0"}
    }.get(style, {"primary": "#d63384", "secondary": "#fd7e14", "accent": "#ffc107", "bg": "#fff5f5"})
    
    title = analysis.get("full_name") or analysis.get("username", "Неизвестный герой")
    subtitle = {
        "romantic": "Наша история любви",
        "fantasy": "Эпическая хроника героя",
        "humor": "Смешная биография"
    }.get(style, "Персональная история")
    
    if style == "fantasy":
        chapters = [{"title": "Древнее пророчество", "subtitle": "Звезды предсказали появление героя", "content": generate_fantasy_chapter(analysis, "prophecy")}, ...]
    elif style == "humor":
        chapters = [{"title": "Знакомьтесь, комедиант", "subtitle": "Человек, который умеет рассмешить всех", "content": generate_humor_chapter(analysis, "introduction")}, ...]
    else:  # romantic
        chapters = [
            {"title": "Тот вечер, что остановил время", "subtitle": "Когда наши взгляды встретились", "content": generate_romantic_chapter(analysis, "meeting")},
            {"title": "Когда мир замолчал", "subtitle": "Магия особенных моментов", "content": generate_romantic_chapter(analysis, "magic")},
            {"title": "Секреты большого сердца", "subtitle": "То, что делает тебя особенным", "content": generate_romantic_chapter(analysis, "secrets")},
            {"title": "Мечты, что стали реальностью", "subtitle": "Романтические грезы воплощаются", "content": generate_romantic_chapter(analysis, "dreams")},
            {"title": "Драгоценные воспоминания", "subtitle": "Моменты, что согревают душу", "content": generate_romantic_chapter(analysis, "memories")},
            {"title": "Слова, идущие от сердца", "subtitle": "Искренние признания", "content": generate_romantic_chapter(analysis, "confessions")},
            {"title": "Вместе навстречу приключениям", "subtitle": "Совместные открытия мира", "content": generate_romantic_chapter(analysis, "adventures")},
            {"title": "Любовь без границ времени", "subtitle": "Чувство, что длится вечность", "content": generate_romantic_chapter(analysis, "eternal")},
            {"title": "И жили они долго и счастливо", "subtitle": "Наш счастливый финал", "content": generate_romantic_chapter(analysis, "finale")}
        ]

    # 2. Генерируем HTML страниц
    pages_html = create_magazine_pages(chapters, images, style, palette, title, subtitle)
    
    # 3. Собираем финальный HTML-документ
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {subtitle}</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lora:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/turn.js@4.1.0/turn.min.js"></script>
    <style>
        body {{
            background: #e0e0e0;
            font-family: 'Lora', serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 2rem 0;
            flex-direction: column;
        }}
        .book-container {{
            position: relative;
        }}
        #flipbook {{
            width: 1200px;
            height: 800px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        .page {{
            background-color: #fdfdfd;
            background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAMAAAAp4XiDAAAAUVBMVEWFhYWDg4N3d3dtbW17e3t1dXWBgYGHh4d5eXlzc3OLi4ubm5uVlZWPj4+NjY19fX2JiYl/f39tbW1+fn5oaGhxcXFra2uBgYGNjY1qampsbGxpaWlnZ2d4eHgtAbCaAAAAB3RSTlMAAAAAsEkNDgAAAAFiS0dEAIgFHUgAAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfiARwAORo2LSZaAAAAVklEQVRIx+3MyQnAIBAD0KaBAggQ9Add/v/aRe9gQN0G9DT1py5lS9wWe1g5I+SYga betyBfB4YoWAN6JVb8H3gLwAEwwIw1A5qnLRC8H1guAAAAAElFTkSuQmCC");
            background-repeat: repeat;
            position: relative;
        }}
        .page::before {{
            content: "";
            position: absolute;
            top: 10px; right: 10px;
            width: 20px; height: 20px;
            border-top: 2px solid rgba(0,0,0,0.1);
            border-right: 2px solid rgba(0,0,0,0.1);
        }}
        .cover, .back-cover {{
            background: linear-gradient(135deg, {palette['primary']}, {palette['secondary']});
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        .cover h1 {{ font-family: 'Playfair Display', serif; font-size: 4rem; font-weight: 700; text-shadow: 2px 2px 5px rgba(0,0,0,0.3); }}
        .cover p {{ font-size: 1.5rem; font-style: italic; opacity: 0.9; }}
        .chapter-left {{ padding: 4rem; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: {palette['bg']};}}
        .chapter-left h2 {{ font-family: 'Playfair Display', serif; font-size: 3rem; color: {palette['primary']}; margin-bottom: 1rem; }}
        .chapter-left p {{ font-style: italic; color: #777; margin-bottom: 2rem; }}
        .chapter-left img {{ max-width: 80%; border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .chapter-right {{ padding: 4rem; column-count: 2; column-gap: 3rem; text-align: justify; }}
        .dropcap {{ float: left; font-size: 4rem; line-height: 0.8; margin: 0.1em 0.1em 0 0; color: {palette['primary']}; font-family: 'Playfair Display', serif; }}
        .pull-quote {{ font-style: italic; border-left: 3px solid {palette['secondary']}; padding-left: 1rem; margin: 1.5rem 0; color: {palette['primary']}; column-span: all; font-size: 1.2rem; }}
        .navigation {{ text-align: center; margin-top: 1.5rem; }}
        .navigation button {{ background: #fff; border: 1px solid #ccc; padding: 10px 20px; cursor: pointer; font-size: 1rem; margin: 0 10px; border-radius: 5px; }}
        .navigation button:hover {{ background: #f0f0f0; }}
        .toc-page {{ padding: 4rem; }}
        .toc-page h2 {{ text-align: center; font-family: 'Playfair Display'; font-size: 3rem; color: {palette['primary']}; margin-bottom: 2rem; }}
        .toc-item {{ border-bottom: 1px dotted #ccc; padding: 1rem 0; display: flex; justify-content: space-between; cursor: pointer; }}
        .toc-item:hover {{ background: {palette['bg']}; }}

        @media print {{
            body {{ background: #fff; padding: 0; }}
            .navigation {{ display: none; }}
            #flipbook {{ display: block; width: auto; height: auto; box-shadow: none; }}
            .page {{ 
                float: none !important;
                display: block !important;
                width: 100% !important;
                height: 100% !important;
                page-break-after: always;
                box-shadow: none !important;
                transform: none !important;
                position: relative !important;
                background-image: none;
                margin: 0;
            }}
            .page:last-child {{ page-break-after: auto; }}
        }}
    </style>
</head>
<body>
    <div class="book-container">
        <div id="flipbook">
            {pages_html}
        </div>
        <div class="navigation">
            <button id="prev">←</button>
            <button id="next">→</button>
        </div>
    </div>
    <script>
        $(function(){{
            $("#flipbook").turn({{
                width: 1200,
                height: 800,
                autoCenter: true,
                acceleration: true,
                gradients: true,
                swipe: true
            }});
            $('#prev').click(()=>$('#flipbook').turn('previous'));
            $('#next').click(()=>$('#flipbook').turn('next'));
            $('.toc-item').on('click', function() {{
                const pageNum = $(this).data('page');
                $('#flipbook').turn('page', pageNum);
            }});
        }});
    </script>
</body>
</html>"""

def create_magazine_pages(chapters: list, images: list, style: str, palette: dict, title: str, subtitle: str) -> str:
    """Создает все страницы для flip-book формата, как отдельные страницы."""
    pages_html = ""

    # 1. Обложка
    pages_html += f'<div class="page cover"><div><h1>{title}</h1><p>{subtitle}</p></div></div>'
    
    # 2. Пустая страница напротив обложки (для правильного разворота)
    pages_html += '<div class="page"></div>'

    # 3. Оглавление
    toc_items_html = ""
    for i, chapter in enumerate(chapters):
        # Левая страница главы - это 2*i + 3, правая - 2*i + 4
        page_num_for_chapter = 2 * i + 5 
        toc_items_html += f'<div class="toc-item" data-page="{page_num_for_chapter}"><span>{i+1}. {chapter["title"]}</span> <span>{page_num_for_chapter}</span></div>'
    pages_html += f'<div class="page toc-page"><h2>Содержание</h2>{toc_items_html}</div>'
    
    # 4. Пустая страница напротив оглавления
    pages_html += '<div class="page"></div>'

    # 5. Развороты глав (каждая глава - это левая + правая страница)
    for i, chapter in enumerate(chapters):
        # Левая страница (заголовок, подзаголовок, фото)
        chapter_image_html = create_photo_collage(images, i)
        pages_html += f"""
        <div class="page chapter-left">
            <h2>{chapter['title']}</h2>
            <p>{chapter['subtitle']}</p>
            {chapter_image_html}
        </div>
        """
        
        # Правая страница (текст главы)
        content = chapter['content']
        if content.startswith('<p>'):
            first_char = content[3]
            content = f'<p><span class="dropcap">{first_char}</span>{content[4:]}'
        
        paragraphs = content.split('</p>')
        if len(paragraphs) > 2:
            mid_point = len(paragraphs) // 2
            quote = generate_chapter_quote(chapter['title'], style)
            paragraphs.insert(mid_point, f'<aside class="pull-quote">"{quote}"</aside>')
            content = '</p>'.join(paragraphs)

        pages_html += f'<div class="page chapter-right">{content}</div>'

    # 6. Задняя обложка
    # Проверяем, нужно ли добавить пустую страницу для правильного разворота
    if (4 + len(chapters) * 2) % 2 != 0:
        pages_html += '<div class="page"></div>'
    pages_html += '<div class="page back-cover"><div><h2>The End</h2></div></div>'
    
    return pages_html

def create_photo_collage(images: list, chapter_index: int) -> str:
    """Создает коллаж из фотографий для журнальной страницы, циклично используя изображения."""
    if not images:
        return '<img src="https://via.placeholder.com/400x300.png?text=Photo" alt="Placeholder">'
    
    num_images = len(images)
    img_idx = chapter_index % num_images
    return f'<img src="{images[img_idx]}" alt="Фотография {img_idx + 1}">'

def generate_chapter_quote(title: str, style: str) -> str:
    """Генерирует цитату для главы"""
    quotes = {
        "romantic": [
            "Любовь — это когда два сердца бьются в унисон",
            "В каждом взгляде — целая вселенная чувств",
            "Настоящая любовь не знает границ времени",
            "Сердце помнит то, что разум забывает"
        ],
        "fantasy": [
            "Магия живет в тех, кто верит в невозможное",
            "Каждый герой начинает с одного шага",
            "Сила не в мече, а в духе воина",
            "Древние тайны открываются достойным"
        ],
        "humor": [
            "Смех — лучшее лекарство от всех бед",
            "Жизнь слишком коротка, чтобы не смеяться",
            "Юмор — это способ смотреть на мир с улыбкой",
            "Каждый день — повод для новой шутки"
        ]
    }
    
    return random.choice(quotes.get(style, quotes["romantic"]))

def generate_fantasy_chapter(analysis: dict, chapter_type: str) -> str:
    """Генерирует содержимое фэнтези главы"""
    name = analysis.get("full_name", "Герой")
    
    content_templates = {
        "prophecy": f"<p>В древних свитках было предсказано появление {name} — героя, чья судьба изменит мир. Звезды сложились в особый узор в день рождения этого великого воина.</p><p>Мудрецы говорили, что {name} обладает редким даром — способностью видеть красоту в обычном и находить магию в повседневности. Этот дар проявляется в каждом поступке, в каждом слове.</p>",
        "kingdom": f"<p>Королевство, где правит {name}, не имеет границ на карте — оно существует в сердцах тех, кто верит в добро и красоту. Здесь каждый день приносит новые открытия и удивительные встречи.</p><p>Подданные этого волшебного королевства — друзья и близкие, которые ценят искренность и доброту своего правителя. Вместе они создают мир, полный смеха и радости.</p>",
        "wisdom": f"<p>Древняя мудрость гласит: истинная сила {name} заключается не в магических заклинаниях, а в умении быть собой. Каждое фото, каждый пост — это заклинание, которое дарит радость другим.</p><p>Мудрость приходит с опытом, и {name} щедро делится своими знаниями с миром, показывая, что настоящая магия — это способность вдохновлять окружающих.</p>"
    }
    
    return content_templates.get(chapter_type, f"<p>Глава о {name} и удивительных приключениях в мире фэнтези.</p>")

def generate_humor_chapter(analysis: dict, chapter_type: str) -> str:
    """Генерирует содержимое юмористической главы"""
    name = analysis.get("full_name", "Комедиант")
    
    content_templates = {
        "introduction": f"<p>Знакомьтесь: {name} — человек, который может рассмешить даже самого серьезного человека! Обладатель уникального таланта находить веселье в самых обычных ситуациях.</p><p>Друзья говорят, что {name} — это живая энциклопедия анекдотов и забавных историй. Каждая встреча с этим человеком превращается в маленький праздник.</p>",
        "daily": f"<p>Обычный день {name} начинается с улыбки и заканчивается смехом. Даже поход в магазин может превратиться в комедийное шоу, если в нем участвует наш герой.</p><p>Умение видеть смешное в повседневности — это особый дар, которым {name} щедро делится с окружающими через социальные сети и живое общение.</p>",
        "social": f"<p>Социальные сети {name} — это настоящая сокровищница юмора! Каждый пост — маленький шедевр, способный поднять настроение даже в самый пасмурный день.</p><p>Подписчики ждут новых публикаций как дети ждут праздника. Ведь {name} умеет превратить обычную фотографию в повод для смеха и радости.</p>"
    }
    
    return content_templates.get(chapter_type, f"<p>Веселая глава о {name} и их удивительном чувстве юмора.</p>")

def generate_romantic_chapter(analysis: dict, chapter_type: str) -> str:
    """Генерирует содержимое романтической главы"""
    name = analysis.get("full_name", "Возлюбленный")
    
    content_templates = {
        "meeting": f"<p>Первая встреча с {name} была как сцена из романтического фильма. Время словно остановилось, и весь мир сузился до одного единственного момента — момента, когда наши взгляды встретились.</p><p>В этих глазах читалась целая история — история доброты, искренности и той особой магии, которая делает человека неповторимым.</p>",
        "magic": f"<p>Магия {name} заключается в умении делать особенными самые обычные моменты. Каждая фотография, каждая улыбка — это маленькое чудо, которое дарит тепло сердцу.</p><p>Есть люди, которые освещают мир своим присутствием, и {name} — именно такой человек. Рядом с ним жизнь становится ярче и полнее.</p>",
        "secrets": f"<p>Сердечные тайны {name} раскрываются не в словах, а в поступках. В том, как заботливо относится к близким, как искренне радуется чужим успехам, как умеет поддержать в трудную минуту.</p><p>Эти маленькие секреты большого сердца делают {name} таким особенным и дорогим для всех, кто имеет счастье быть рядом.</p>"
    }
    
    return content_templates.get(chapter_type, f"<p>Романтическая глава о {name} и особенных моментах жизни.</p>")

def add_magazine_styling():
    pass 