import base64
from pathlib import Path
from app.config import settings
from typing import Optional
import logging
import random
from openai import OpenAI

# Инициализация Azure OpenAI
client = OpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    base_url=settings.AZURE_OPENAI_ENDPOINT,
    default_headers={"api-key": settings.AZURE_OPENAI_API_KEY}
)

logger = logging.getLogger(__name__)

# Автоматическое удаление клише
CLICHE_FILTERS = [
    "мягкие оттенки", "резкие тени", "атмосфера", "ощущение",
    "передает эмоции", "придает глубину", "создает настроение",
    "особая атмосфера", "уникальная история", "снимок показывает"
]

def strip_cliches(text: str) -> str:
    """Убирает шаблонные фразы из текста"""
    for cliche in CLICHE_FILTERS:
        text = text.replace(cliche, "")
    
    # Убираем markdown форматирование
    text = text.replace("**", "")  # Жирный текст
    text = text.replace("***", "")  # Жирный курсив
    text = text.replace("*", "")   # Курсив/выделение
    text = text.replace("__", "")  # Альтернативный жирный
    text = text.replace("_", "")   # Альтернативный курсив
    text = text.replace("~~", "")  # Зачеркивание
    text = text.replace("```", "") # Блоки кода
    text = text.replace("`", "")   # Инлайн код
    text = text.replace("##", "")  # Заголовки
    text = text.replace("#", "")   # Заголовки
    
    # Убираем лишние символы
    text = text.replace("---", "")  # Разделители
    text = text.replace("–", "-")   # Длинное тире на обычное
    text = text.replace("—", "-")   # Еще длиннее тире
    
    # Убираем двойные пробелы и переносы
    text = " ".join(text.split())
    return text

def generate_text(prompt: str,
                  model: str = "gpt-4o",
                  max_tokens: int = 400,  # Снижено с 1500 до 400 для скорости
                  temperature: float = 0.7,  # Снижено с 0.8 до 0.7 для более быстрых ответов
                  image_data: Optional[str] = None) -> str:
    """Генерирует текст с помощью Azure OpenAI API (только GPT-4o), с поддержкой изображений"""
    try:
        # Всегда используем GPT-4o deployment
        deployment = settings.AZURE_OPENAI_GPT4_DEPLOYMENT
        
        # БЫСТРАЯ система для романтического рассказчика (сокращенная версия)
        fast_system_message = """Ты - романтический рассказчик. Пиши просто, искренне, романтично.

СТИЛЬ: Дневник влюбленного
ЯЗЫК: Русский, простой, теплый
ДЛИНА: Кратко, по сути

ЗАПРЕЩЕНО: "Не могу поверить!", "Потрясающе!", сложные фразы"""

        # Если есть изображение, используем vision model
        if image_data:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data,
                                "detail": "low"  # Для определения пола достаточно низкого качества
                            }
                        }
                    ]
                }
            ]

            response = client.chat.completions.create(
                model=deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
        else:
            # Обычная генерация текста (БЫСТРАЯ)
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": fast_system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.3,  # Снижено для скорости
                frequency_penalty=0.2  # Снижено для скорости
            )
        
        result = response.choices[0].message.content.strip()
        return strip_cliches(result)
        
    except Exception as e:
        logger.error(f"Ошибка в generate_text: {e}")
        # Быстрый fallback вместо ошибки
        return f"Этот момент наполнен особой красотой и теплом. Каждая деталь говорит о твоей уникальности."


def analyze_photo_for_memoir(image_path: Path, context: str = "", chapter_focus: str = "general") -> str:
    """Анализирует фотографию для мемуарного повествования"""
    try:
        if not image_path.exists():
            return "В памяти остался лишь размытый силуэт..."
            
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Фокусы для разных глав
        chapter_styles = {
            "first_impression": """Опиши ПЕРВОЕ впечатление от фотографии как воспоминание:

Включи обязательно:
- Что первым бросилось в глаза (цвет, свет, деталь)
- Какой звук/запах/ощущение пришло в голову
- Одну внутреннюю реплику в кавычках
- Одну метафору

Пиши от первого лица как запись в дневнике.
Максимум 4 предложения.""",

            "story_creation": """Создай мини-новеллу по фотографии (до 3 абзацев):

1-й абзац: Что происходило ДО этого кадра
2-й абзац: Момент съёмки (включи 3 сенсорные детали)
3-й абзац: Что чувствовал человек ПОСЛЕ

Пиши как будто ты был свидетелем этой сцены.
Включи один диалог или внутренний монолог.""",

            "hidden_emotions": """Прочитай между строк фотографии:

Что скрывается за идеальным кадром?
- Какое настроение было на самом деле?
- О чём думал человек в этот момент?
- Что он НЕ показал в кадре?

Пиши лирически, включи 2-3 чувственные детали.
Как психологический портрет."""
        }
        
        style = chapter_styles.get(chapter_focus, chapter_styles["first_impression"])
        
        prompt = f"""{style}

Контекст профиля: {context}

Пиши романтично и поэтично, но искренне.
Избегай клише!"""

        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_GPT4_DEPLOYMENT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.9
        )
        
        result = response.choices[0].message.content.strip()
        return strip_cliches(result)
        
    except Exception as e:
        logger.error(f"Ошибка анализа фото {image_path}: {e}")
        return f"Память сохранила лишь ощущение света и тепла..."


def generate_memoir_chapter(chapter_type: str, data: dict, photo_analysis: str = "") -> str:
    """Генерирует главу мемуаров по конкретной структуре"""
    
    # Проверяем, передан ли готовый промпт в данных
    if chapter_type == "romantic_book_chapter" and "prompt" in data:
        # Для романтических книг используем переданный промпт
        prompt = data["prompt"]
        
        # КРИТИЧЕСКАЯ ОПТИМИЗАЦИЯ: сокращаем все промпты в 3-4 раза
        # Берем только первые 500 символов промпта для быстрого ответа
        if len(prompt) > 500:
            # Находим конец первого абзаца с инструкциями
            cut_point = prompt.find("СТРУКТУРА ГЛАВЫ:")
            if cut_point > 0:
                prompt = prompt[:cut_point] + "\n\nНапиши 3-4 абзаца романтично и лично."
            else:
                prompt = prompt[:500] + "... Напиши кратко и романтично."
        
        result = generate_text(prompt, max_tokens=400, temperature=0.7)  # Снижено с 1500 до 400
        return strip_cliches(result)
    
    username = data.get('username', 'незнакомец')
    followers = data.get('followers', 0)
    captions = data.get('captions', ['Без слов'])
    bio = data.get('bio', '')
    locations = data.get('locations', ['неизвестное место'])
    
    # БЫСТРЫЕ КОРОТКИЕ ПРОМПТЫ вместо длинных
    quick_prompts = {
        "meeting": f"""Напиши 3 абзаца о знакомстве с @{username}:

1. "Дорогой {username}, листая Instagram, я увидел твой профиль..."
2. Что зацепило с первого взгляда
3. Почему остановился изучать дальше

Пиши романтично, от первого лица. Подпись: "{captions[0] if captions else 'твоя подпись'}"

Максимум 300 слов.""",

        "first_impression": f"""Напиши 3 абзаца о первых впечатлениях от @{username}:

1. "Что меня поразило в твоем профиле..."
2. Описание внешности - глаза, улыбка, черты лица  
3. Общее впечатление об искренности

Стиль: романтично, лично. Максимум 250 слов.""",

        "world_view": f"""Напиши 3 абзаца о том, как @{username} видит мир:

1. "Больше всего поражает, как ты видишь мир..."
2. Анализ фотографий и композиции
3. Связь внешности и внутреннего мира

БИО: "{bio if bio else 'Молчание говорит о многом'}"
Максимум 250 слов.""",

        "memorable_moments": f"""Напиши 3 абзаца о запомнившихся моментах @{username}:

1. "Есть кадры, которые врезались в память..."
2. Конкретная фотография и впечатления
3. Искренность эмоций в глазах

Подпись: "{captions[0] if captions else '🤠'}"
Максимум 250 слов.""",

        "energy": f"""Напиши 3 абзаца об энергетике @{username}:

1. "В тебе особая энергетика..."
2. Естественность и харизма
3. Описание - кожа, волосы, движения

Стиль: восхищение. Максимум 250 слов.""",

        "beauty_style": f"""Напиши 3 абзаца о красоте @{username}:

1. "Красота в твоем случае очевидна..."
2. Лицо как произведение искусства
3. Брови, ресницы, улыбка

Стиль: поэтично. Максимум 250 слов.""",

        "mystery": f"""Напиши 3 абзаца о загадочности @{username}:

1. "В тебе особая загадочность..."
2. Взгляд и предположения о голосе
3. Походка и манеры

Стиль: интрига. Максимум 250 слов.""",

        "influence_on_me": f"""Напиши 3 абзаца о влиянии @{username}:

1. "Ты изменил мой взгляд на многое..."
2. Новое внимание к деталям
3. Благодарность за уроки

Подпись: "{captions[0] if captions else 'твоя подпись'}"
Максимум 250 слов.""",

        "observations": f"""Напиши 3 абзаца о наблюдениях за @{username}:

1. "Сделал интересные открытия..."
2. Фотогеничность и руки
3. Любовь к свету и осанка

Стиль: наблюдения. Максимум 250 слов.""",

        "gratitude_wishes": f"""Напиши 4 абзаца благодарности {username}:

1. "Книга подходит к концу..."
2. Пожелания быть собой
3. Пожелания любви и счастья  
4. "Спасибо, что ты есть. Твой поклонник."

БИО: "{bio if bio else 'особенная натура'}"
Максимум 300 слов."""
    }
    
    # Fallback контент на случай ошибок ИИ
    fallback_content = {
        "meeting": f"Дорогой {username}, листая Instagram, я случайно наткнулся на твой профиль. Что-то в твоем взгляде заставило остановиться и изучать каждое фото внимательнее. Возможно, это была искренность, которой так не хватает в мире фильтров.",
        
        "first_impression": f"Первое, что поразило в твоем профиле - это естественность. Каждое фото рассказывает историю, а твои глаза особенно выразительны. В них читается ум, доброта и глубина души. Твоя улыбка освещает все вокруг.",
        
        "world_view": f"Больше всего поражает то, как ты видишь мир вокруг себя. У тебя есть дар находить прекрасное в обыденном. Твоя внешность отражает внутренний мир - ты красив естественной красотой.",
        
        "memorable_moments": f"Есть кадры, которые врезались в память навсегда. Твоя красота живая, меняющаяся. Твои глаза - отдельная поэма, глубокие и выразительные. Искренность - твое главное качество.",
        
        "energy": f"В тебе есть особая энергетика, которая чувствуется даже через экран. Умеешь быть собой в любой ситуации. У тебя красивая кожа, волосы, движения полны грации.",
        
        "beauty_style": f"Красота в твоем случае очевидна для всех. Твое лицо - произведение искусства с правильными пропорциями. Красивые брови, длинные ресницы, безупречная кожа.",
        
        "mystery": f"В тебе особая загадочность, которая не дает покоя. Каждый кадр открывает что-то новое. Твой взгляд загадочен, в нем глубина океана.",
        
        "influence_on_me": f"Ты изменил мой взгляд на многие вещи. Стал больше внимания обращать на детали вокруг. Показал, что красота не требует дорогих декораций.",
        
        "observations": f"За время наблюдения сделал интересные открытия. Твое лицо очень фотогеничное, выразительные руки. Любишь свет и умело его используешь.",
        
        "gratitude_wishes": f"{username}, эта книга подходит к концу, но восхищение остается. Продолжай быть собой, желаю любви и счастья. Спасибо за то, что ты есть. Твой поклонник."
    }
    
    # Быстрая генерация с таймаутом
    try:
        prompt = quick_prompts.get(chapter_type, f"Напиши романтично о {chapter_type.replace('_', ' ')}.")
        result = generate_text(prompt, max_tokens=300, temperature=0.7)  # Быстрые настройки
        
        # Проверяем качество результата
        if len(result.strip()) < 50:  # Если слишком короткий ответ
            return fallback_content.get(chapter_type, f"Глава о {chapter_type.replace('_', ' ')} наполнена теплом и восхищением.")
            
        return strip_cliches(result)
        
    except Exception as e:
        print(f"⚡ Быстрый fallback для главы '{chapter_type}': {e}")
        return fallback_content.get(chapter_type, f"Эта глава о {chapter_type.replace('_', ' ')} написана с особой нежностью.")


def generate_complete_memoir_book(data: dict, images: list) -> dict:
    """Генерирует все 10 глав мемуаров для полноценной романтической книги"""
    
    username = data.get('username', 'незнакомец')
    
    # Анализируем фотографии для разных глав
    photo_analyses = []
    if images:
        for i, img_path in enumerate(images[:10]):  # Максимум 10 фото для анализа
            if img_path.exists():
                try:
                    focus_types = ["first_impression", "story_creation", "hidden_emotions"]
                    focus = focus_types[i % 3]
                    analysis = analyze_photo_for_memoir(img_path, f"@{username}", focus)
                    photo_analyses.append(analysis)
                except Exception as e:
                    print(f"❌ Ошибка анализа фото {img_path}: {e}")
                    photo_analyses.append("Фотография пробуждает особые чувства...")
    
    # Добавляем анализы фото в данные
    data['photo_analyses'] = photo_analyses
    
    # Генерируем все 10 глав
    chapters = {}
    
    chapter_types = [
        "meeting", "first_impression", "world_view", "memorable_moments", 
        "energy", "beauty_style", "mystery", "influence_on_me", 
        "observations", "gratitude_wishes"
    ]
    
    for chapter_type in chapter_types:
        try:
            photo_analysis = ""
            if chapter_type in ["first_impression", "memorable_moments"] and photo_analyses:
                photo_analysis = photo_analyses[0] if photo_analyses else ""
            
            chapter_content = generate_memoir_chapter(chapter_type, data, photo_analysis)
            chapters[chapter_type] = chapter_content
            print(f"✅ Глава '{chapter_type}' создана")
            
        except Exception as e:
            print(f"❌ Ошибка создания главы '{chapter_type}': {e}")
            # Добавляем базовый контент при ошибке
            chapters[chapter_type] = f"Глава о {chapter_type.replace('_', ' ')} ждет своего написания..."
    
    return chapters
