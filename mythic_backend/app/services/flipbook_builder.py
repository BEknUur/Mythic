# app/services/flipbook_builder.py
import json
import re
import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import markdown
from app.services.llm_client import generate_text
from app.services.book_builder import analyze_profile_data

# подключаем шаблоны из папки app/templates
env = Environment(loader=FileSystemLoader('app/templates'))

def strip_hashtags(text: str) -> str:
    """Убираем все #хэштеги из текста"""
    return re.sub(r'\B#\w+\b', '', text).strip()

def generate_pages_html(run_id: str, image_paths: list[str], text_pages: list[str]) -> list[str]:
    """
    Генерирует HTML-страницы для флипбука в формате "разворотов": текст слева, фото справа.
    """
    print("📚 Собираю страницы для флипбука в новом формате...")
    
    pages = []

    # ========== ОБЛОЖКА ==========
    pages.append("""
      <div class="cover-page">
        <h1>Романтическая<br>История</h1>
        <p><i>С любовью создано для тебя...</i></p>
        <div class="cover-decoration">💕</div>
      </div>
    """)

    # ========== ТИТУЛЬНЫЙ ЛИСТ ==========
    pages.append("""
        <div class="page-content title-page">
            <h1>Романтическая<br>История</h1>
            <p>создано с любовью и восхищением</p>
            <div class="title-decoration">
                <div class="heart">♥</div>
                <div class="date">""" + f"{datetime.datetime.now().strftime('%B %Y')}" + """</div>
            </div>
        </div>
    """)

    # ========== ЗАГРУЖАЕМ ПРОФИЛЬ ДЛЯ КОНТЕКСТА ==========
    profile_path = Path("data") / run_id / "posts.json"
    profile_data = []
    if profile_path.exists():
        try:
            profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"⚠️ Не удалось прочитать posts.json: {e}")

    profile_ctx = analyze_profile_data(profile_data) if profile_data else {}
    full_name = profile_ctx.get("full_name") or profile_ctx.get("username") or "этого человека"
    raw_comments = [post.get("caption", "") for post in profile_data[0].get("latestPosts", [])] if profile_data else []

    # ========== ПРОЛОГ ==========
    prologue = generate_section_text(
        role="Пролог",
        full_name=full_name,
        prompt=f"""Напиши проникновенный пролог (120-150 слов) к романтической книге 
        о человеке по имени {full_name}. Пиши тепло, личностно, как влюблённый человек.
        Используй 'ты' обращение. Пусть это будет началом красивой истории."""
    )
    
    pages.append(f"""
      <div class="page-content text-content prologue">
        <h2>Пролог</h2>
        {markdown.markdown(prologue)}
      </div>
    """)

    # ========== ОГЛАВЛЕНИЕ ==========
    # Генерируем краткие описания глав
    toc_summaries = generate_toc_summaries(
        full_name=full_name,
        image_count=len(image_paths),
        raw_comments=raw_comments
    )
    
    toc_items = "".join(f"<li>{summary}</li>" for summary in toc_summaries)
    pages.append(f"""
      <div class="page-content toc-page">
        <h2>Содержание</h2>
        <ol class="toc">{toc_items}</ol>
      </div>
    """)

    # ========== ОСНОВНЫЕ РАЗВОРОТЫ (ТЕКСТ + ФОТО) ==========
    # Если текстовых страниц мало, делим первую на части
    if len(text_pages) < 12 and text_pages:
        first_text = strip_hashtags(text_pages[0])
        words = first_text.split()
        if len(words) > 300:  # Только если есть что делить
            chunk_size = max(150, len(words)//10)
            new_pages = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            text_pages = new_pages[:12] + text_pages[1:]

    for idx, img_path in enumerate(image_paths):
        # Получаем исходный текст и очищаем от хэштегов
        raw_text = text_pages[idx] if idx < len(text_pages) else ""
        raw_text = strip_hashtags(raw_text)

        # Если текста мало (<350 символов) — генерируем заново через LLM
        if len(raw_text.strip()) < 350:
            try:
                prompt = f"""Ты — романтический писатель. Напиши 5-6 абзацев (≈500-600 слов) для страницы флипбука о {full_name}. 
                Это текст к фотографии №{idx+1}. Должно звучать лично, тепло, поэтично, обращайся на "ты". 
                Свяжи рассказ с предыдущими страницами и создавай непрерывную историю. 
                Пиши на русском. Используй стиль дневника влюблённого, избегай штампов и клише.
                Описывай не только то, что видно на фото, но и чувства, эмоции, воспоминания."""
                
                raw_text = generate_text(prompt, max_tokens=1800, temperature=0.85)
                print(f"💬 LLM сгенерировал расширенный текст для страницы {idx+1} (длина {len(raw_text)} символов)")
            except Exception as e:
                print(f"⚠️ Ошибка LLM при генерации текста для страницы {idx+1}: {e}")
                print(f"📝 Используется fallback текст для страницы {idx+1}")
                
                # Создаем красивые fallback тексты для каждой страницы
                fallback_texts = [
                    f"""Эта фотография открывает историю {full_name} — человека, который умеет находить красоту в каждом моменте.

                    Взгляни на этот кадр — здесь столько искренности и естественности. Каждая деталь говорит о том, как {full_name} проживает свою жизнь: ярко, смело, с открытым сердцем.

                    В этом снимке можно увидеть не просто момент, а частичку души. Энергия, которая исходит от {full_name}, согревает всех вокруг и делает обычный день особенным.

                    Это начало удивительной истории о человеке, который дарит миру свет просто тем, что существует.""",
                    
                    f"""Каждый новый день в жизни {full_name} — это новое приключение, новая возможность удивлять мир своей искренностью.

                    На этой фотографии время словно замерло, запечатлев тот самый момент, когда счастье становится видимым. Улыбка, взгляд, каждый жест — всё говорит о том, что жизнь прекрасна.

                    {full_name} обладает удивительным даром — превращать обычные мгновения в воспоминания, которые будут согревать сердце годами. Эта способность видеть красоту там, где другие проходят мимо, делает каждую встречу с {full_name} особенной.

                    Этот кадр — свидетельство того, как важно уметь радоваться простым вещам.""",
                    
                    f"""Время течёт, но некоторые моменты остаются с нами навсегда. Эта фотография — один из таких моментов в жизни {full_name}.

                    Здесь запечатлена не просто сцена из жизни, а эмоция, которая передаётся через экран. Когда смотришь на {full_name}, понимаешь, что настоящая красота — это не внешность, а внутренний свет, который невозможно скрыть.

                    Каждый день {full_name} доказывает, что жизнь стоит того, чтобы её проживать полно и ярко. Этот снимок — маленькое окно в мир, где каждый момент ценится и помнится.

                    Такие люди, как {full_name}, напоминают нам, что счастье — это не цель, а способ жизни."""
                ]
                
                # Циклически выбираем тексты для разных страниц
                selected_text = fallback_texts[idx % len(fallback_texts)]
                raw_text = raw_text or selected_text

        # Левая страница — Текст
        html_txt = markdown.markdown(raw_text)
        pages.append(f"""
          <div class="page-content text-content chapter">
            <h3>Глава {idx+1}</h3>
            {html_txt}
          </div>
        """)

        # Правая страница — Изображение
        fn = Path(img_path).name
        pages.append(f"""
          <div class="page-image">
            <img src="/data/{run_id}/images/{fn}" 
                 alt="Фотография {idx+1}" 
                 onerror="this.onerror=null;this.src='/static/img/fallback.jpg';"/>
            <div class="image-caption">Глава {idx+1}</div>
          </div>
        """)
        
    # ========== ЭПИЛОГ ==========
    epilogue = generate_section_text(
        role="Эпилог",
        full_name=full_name,
        prompt=f"""Напиши тёплый эпилог (100-120 слов) к романтической книге о {full_name}, 
        подытоживающий всё, что было рассказано. Пусть это будет красивое завершение истории,
        полное надежды и любви."""
    )
    
    pages.append(f"""
      <div class="page-content text-content epilogue">
        <h2>Эпилог</h2>
        {markdown.markdown(epilogue)}
        <div class="final-decoration">
          <div class="hearts">💕 ♥ 💕</div>
          <p><i>Конец — это всегда новое начало...</i></p>
        </div>
      </div>
    """)

    print(f"📚 Создано {len(pages)} страниц для флипбука")
    return pages


def generate_section_text(role: str, full_name: str, prompt: str) -> str:
    """Генерирует текст для специальных разделов (пролог, эпилог)"""
    try:
        return generate_text(
            prompt=prompt,
            max_tokens=800,
            temperature=0.9
        )
    except Exception as e:
        print(f"⚠️ Ошибка при генерации {role}: {e}")
        print(f"📝 Используется fallback текст для {role}")
        
        # Красивые fallback тексты
        if role == "Пролог":
            return f"""Эта книга — о {full_name}, о моментах, которые делают жизнь особенной. 
            
            В каждой фотографии живёт история, в каждом взгляде — частичка души. Мы собрали здесь не просто кадры из жизни, а мгновения, которые останутся в памяти навсегда.
            
            Листая эти страницы, ты увидишь не только красивые картинки, но и почувствуешь ту энергию, ту радость и ту искренность, которую {full_name} дарит миру каждый день.
            
            Это история о том, как обычные моменты становятся особенными, когда их переживает особенный человек."""
            
        elif role == "Эпилог":
            return f"""История {full_name} продолжается каждый день. 
            
            Эта книга — лишь небольшая часть удивительного путешествия длиною в жизнь. Каждая новая фотография — это новая глава, каждый день — новое приключение.
            
            Пусть впереди будет много ярких моментов, искренних улыбок и прекрасных воспоминаний. Пусть жизнь дарит новые поводы для радости и новые истории для следующих книг.
            
            До встречи в новых главах этой удивительной истории!"""
        else:
            return "Этот момент наполнен особой красотой и теплом. Воспоминания живут в сердце навсегда."


def generate_toc_summaries(full_name: str, image_count: int, raw_comments: list) -> list[str]:
    """Генерирует краткие описания для оглавления"""
    try:
        comments_text = " ".join(raw_comments[:10]) if raw_comments else ""
        prompt = f"""Создай {min(image_count, 12)} кратких и поэтичных названий глав для романтической книги о {full_name}.
        Каждое название должно быть в формате "Глава X: Название" (например, "Глава 1: Утренний свет").
        Названия должны быть романтичными, но не банальными. Основывайся на этих подписях из Instagram: {comments_text[:500]}
        
        Выдай только список названий, по одному на строку."""
        
        result = generate_text(prompt, max_tokens=600, temperature=0.8)
        lines = [line.strip() for line in result.split('\n') if line.strip() and 'Глава' in line]
        
        # Если получили меньше названий, чем нужно, дополняем стандартными
        while len(lines) < min(image_count, 12):
            chapter_num = len(lines) + 1
            lines.append(f"Глава {chapter_num}: Особенный момент")
            
        return lines[:min(image_count, 12)]
        
    except Exception as e:
        print(f"⚠️ Ошибка при генерации оглавления: {e}")
        print("📝 Используется fallback оглавление")
        
        # Красивые fallback названия глав
        beautiful_titles = [
            "Первый взгляд", "Утренний свет", "Моменты счастья", "Тёплые воспоминания",
            "Искренняя улыбка", "Яркие краски", "Летний день", "Вечерние мечты",
            "Особенные мгновения", "Радостные открытия", "Душевная гармония", "Прекрасные детали"
        ]
        
        needed_count = min(image_count, 12)
        result = []
        for i in range(needed_count):
            title = beautiful_titles[i % len(beautiful_titles)]
            result.append(f"Глава {i+1}: {title}")
        
        return result


def build_flipbook_html(run_id: str, pages: list[str]):
    """Собирает итоговый HTML флипбука"""
    try:
        tpl = env.get_template('flipbook_template.html')
        html = tpl.render(pages=pages, run_id=run_id)
        out = Path('data') / run_id / 'book.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding='utf-8')
        print(f"✅ Flipbook HTML создан: {out}")
    except Exception as e:
        print(f"❌ Ошибка при создании HTML: {e}")
        raise 