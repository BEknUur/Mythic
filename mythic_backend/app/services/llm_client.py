import base64
from pathlib import Path
from app.config import settings
from typing import Optional
import logging
import random
from openai import AzureOpenAI, AsyncAzureOpenAI
import json
import markdown
from app.services.cache_service import cache_service

# Инициализация синхронного клиента
client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION
)

# Инициализация АСИНХРОННОГО клиента для новых функций
async_client = AsyncAzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION
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

def image_to_base64(image_path: str) -> str:
    """Кодирует изображение в строку Base64 с правильным MIME-типом."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Определяем MIME-тип по расширению файла
        extension = Path(image_path).suffix.lower().replace('.', '')
        if extension == 'jpg':
            extension = 'jpeg'
        
        return f"data:image/{extension};base64,{encoded_string}"
    except Exception as e:
        logger.error(f"❌ Ошибка кодирования изображения {image_path}: {e}")
        return ""

async def generate_flipbook_json(image_paths: list[str]) -> dict:
    """
    Генерирует всю структуру флипбука (пролог и страницы) в виде единого JSON-объекта,
    используя function calling для гарантированной валидности формата.
    """
    # 1. Схема для function calling
    functions = [
        {
            "name": "build_flipbook",
            "description": "Создать контент для флипбука: пролог и страницы с текстом и привязанной картинкой.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prologue": {
                        "type": "string",
                        "description": "Вступительный текст для книги, задающий романтическое настроение."
                    },
                    "pages": {
                        "type": "array",
                        "description": "Массив страниц, где каждая страница содержит текст и имя файла изображения.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Романтический текст, описывающий фотографию."},
                                "image": {"type": "string", "description": "Имя файла изображения для этой страницы."}
                            },
                            "required": ["text", "image"]
                        }
                    }
                },
                "required": ["prologue", "pages"]
            }
        }
    ]

    # 2. Формируем промпт для модели
    # Преобразуем пути в просто имена файлов, как ожидает модель
    image_filenames = [Path(p).name for p in image_paths]
    
    system_prompt = """Ты — поэт-романтик, мастер красивых признаний и вдохновляющих историй.\nТвоя задача — для каждой фотографии героя написать короткую главу (1-2 абзаца, 60-90 слов),\nгде фото — лишь повод для романтического рассказа о человеке: его чувствах, мечтах, характере, отношениях, воспоминаниях, надеждах.\nНе описывай, что изображено на фото буквально!\nПиши так, будто ты влюблён в героя, восхищаешься им, видишь в нём уникальную личность.\nИспользуй красивый, поэтичный, образный язык, метафоры, сравнения, аллюзии.\nОбращайся к герою на «ты» или во втором лице.\nИзбегай банальных описаний, не повторяйся, не используй клише.\nРезультат верни строго в формате JSON, используя функцию `build_flipbook`.\nНе добавляй никаких комментариев или вступлений, только вызов функции.\nИстория должна быть связной и вызывать тёплые чувства."""

    user_prompt = f"Создай фотокнигу на основе следующих изображений: {json.dumps(image_filenames)}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # 3. Вызываем Azure OpenAI API с `function_call`
    try:
        response = await async_client.chat.completions.create(
            model=settings.AZURE_OPENAI_GPT4_DEPLOYMENT, # Используем мощную модель для креатива
            messages=messages,
            functions=functions,
            function_call={"name": "build_flipbook"}, # Принудительно вызываем нашу функцию
            temperature=0.8
        )

        # 4. Извлекаем и парсим JSON из ответа
        function_call_args = response.choices[0].message.function_call.arguments
        if function_call_args:
            flipbook_data = json.loads(function_call_args)
            print("✅ LLM успешно сгенерировал JSON для флипбука.")
            
            # Сопоставляем абсолютные пути с именами файлов
            image_path_map = {Path(p).name: p for p in image_paths}

            # Заменяем имена файлов на Base64
            for page in flipbook_data.get("pages", []):
                image_name = page.get("image")
                if image_name in image_path_map:
                    # Кодируем в Base64 и подставляем в src
                    page["image"] = image_to_base64(image_path_map[image_name])
                else:
                    # Если картинка не найдена, оставляем пустое поле
                    page["image"] = ""
            
            return flipbook_data
        else:
            logger.error("LLM не вернул ожидаемые аргументы функции.")
            return {}

    except Exception as e:
        logger.error(f"❌ Ошибка при вызове LLM с function calling: {e}")
        # В случае ошибки, можно вернуть пустую структуру, чтобы приложение не падало
        return {"prologue": "Что-то пошло не так...", "pages": []}

async def generate_text_async(prompt: str,
                  system_prompt: str | None = None,
                  model: str = "gpt-4.1-mini",
                  max_tokens: int = 1500,
                  temperature: float = 0.8,
                  image_data: Optional[str] = None) -> str:
    """Асинхронная версия generate_text с кэшированием"""
    
    # Создаем ключ кэша на основе параметров
    cache_key_parts = [
        prompt[:100],  # Первые 100 символов промпта
        system_prompt[:50] if system_prompt else "",
        str(max_tokens),
        str(temperature),
        "image" if image_data else "text"
    ]
    cache_key = "ai_response:" + hash("".join(cache_key_parts))
    
    # Пытаемся получить из кэша
    cached_response = await cache_service.get_ai_response(cache_key)
    if cached_response:
        logger.info(f"📦 Кэш HIT для AI ответа")
        return cached_response
    
    try:
        deployment = settings.AZURE_OPENAI_GPT4_DEPLOYMENT
        # Нейтральная система по умолчанию
        fast_system_message = system_prompt or "Ты — современный рассказчик. Пиши ясно, интересно, без клише."
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
                                "detail": "low"
                            }
                        }
                    ]
                }
            ]
            response = await async_client.chat.completions.create(
                model=deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            response = await async_client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": fast_system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.3,
                frequency_penalty=0.2
            )
        result = response.choices[0].message.content
        if not result:
            return ""
        
        final_result = strip_cliches(result.strip())
        
        # Кэшируем результат на 1 час
        await cache_service.cache_ai_response(cache_key, final_result, 3600)
        
        return final_result
    except Exception as e:
        logger.error(f"Ошибка в generate_text_async: {e}")
        return f"Этот момент наполнен особой красотой и теплом. Каждая деталь говорит о твоей уникальности."

def generate_text(prompt: str,
                  system_prompt: str | None = None,   # <-- add system_prompt param
                  model: str = "gpt-4.1-mini",
                  max_tokens: int = 1500,
                  temperature: float = 0.8,
                  image_data: Optional[str] = None) -> str:
    """Генерирует текст с помощью Azure OpenAI API (только GPT-4o), с поддержкой изображений"""
    try:
        deployment = settings.AZURE_OPENAI_GPT4_DEPLOYMENT
        # Нейтральная система по умолчанию
        fast_system_message = system_prompt or "Ты — современный рассказчик. Пиши ясно, интересно, без клише."
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
                                "detail": "low"
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
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": fast_system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.3,
                frequency_penalty=0.2
            )
        result = response.choices[0].message.content
        if not result:
            return ""
        return strip_cliches(result.strip())
    except Exception as e:
        logger.error(f"Ошибка в generate_text: {e}")
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


def generate_memoir_chapter(chapter_type: str, data: dict, photo_analysis: str = "", temperature: float = 0.8, max_tokens: int = 1200) -> str:
    """Генерирует главу мемуаров по конкретной структуре"""
    
    # Проверяем, передан ли готовый промпт в данных
    if chapter_type == "romantic_book_chapter" and "prompt" in data:
        # Для романтических книг используем переданный промпт
        prompt = data["prompt"]
        
        # НЕ обрезаем промпты с пословицами - они уже оптимизированы
        result = generate_text(prompt, max_tokens=max_tokens, temperature=temperature)  # Увеличиваем для качественных текстов
        return strip_cliches(result)
    
    # Поддержка фэнтези стиля
    if chapter_type == "fantasy_chapter" and "prompt" in data:
        prompt = data["prompt"]
        sys_prompt = data.get("system_prompt")  # <-- extract system_prompt if present
        
        # НЕ обрезаем промпты с пословицами - они уже оптимизированы
        result = generate_text(
            prompt, 
            system_prompt=sys_prompt,            # <-- pass system_prompt
            max_tokens=max_tokens, 
            temperature=temperature
        )  # Больше креативности для фэнтези
        return strip_cliches(result)
    
    # Поддержка юмористического стиля
    if chapter_type == "humor_chapter" and "prompt" in data:
        prompt = data["prompt"]
        sys_prompt = data.get("system_prompt")  # <-- extract system_prompt if present
        result = generate_text(
            prompt,
            system_prompt=sys_prompt,            # <-- pass system_prompt
            max_tokens=max_tokens,
            temperature=temperature
        )
        return strip_cliches(result)
    
    username = data.get('username', 'незнакомец')
    followers = data.get('followers', 0)
    captions = data.get('captions', ['Без слов'])
    bio = data.get('bio', '')
    locations = data.get('locations', ['неизвестное место'])
    
    # Улучшенные ДЛИННЫЕ ПРОМПТЫ для качественных текстов
    detailed_prompts = {
        "meeting": f"""Напиши развернутую главу о знакомстве с @{username} (4-5 абзацев):

1. "Дорогой {username}, листая Instagram, я увидел твой профиль..." - как это произошло
2. Первая реакция - что именно зацепило с первого взгляда
3. Детальное описание того, что заставило остановиться
4. Внутренний монолог о том, что этот человек особенный
5. Заключение о решении изучать профиль дальше

Контекст: подписи "{captions[0] if captions else 'твоя подпись'}", {followers} подписчиков

Пиши романтично, от первого лица, детально. Минимум 400 слов.""",

        "first_impression": f"""Напиши развернутую главу о первых впечатлениях от @{username} (4-5 абзацев):

1. "Что меня поразило в твоем профиле больше всего..." - общее впечатление
2. Детальное описание внешности - глаза, их выражение, цвет, глубина
3. Улыбка, черты лица, общая гармония
4. Впечатление об искренности и естественности
5. Заключение о том, что это не просто красота, а что-то большее

Стиль: романтично, лично, поэтично. Минимум 400 слов.""",

        "world_view": f"""Напиши развернутую главу о том, как @{username} видит мир (4-5 абзацев):

1. "Больше всего поражает, как ты видишь мир вокруг себя..." - введение
2. Анализ композиции фотографий и выбора ракурсов
3. Способность находить красоту в обычном
4. Связь между внешностью и внутренним миром
5. Заключение о том, что красота души отражается в облике

БИО: "{bio if bio else 'Молчание говорит о многом'}"
Локации: {', '.join(locations[:3])}

Минимум 400 слов.""",

        "memorable_moments": f"""Напиши развернутую главу о запомнившихся моментах @{username} (4-5 абзацев):

1. "Есть кадры, которые врезались в память навсегда..." - введение
2. Описание конкретной фотографии и впечатлений от неё
3. Анализ эмоций в глазах и выражении лица
4. Искренность и живость красоты
5. Заключение о том, что каждый кадр - отдельная история

Подпись: "{captions[0] if captions else '🤠'}"

Минимум 400 слов.""",

        "energy": f"""Напиши развернутую главу об энергетике @{username} (4-5 абзацев):

1. "В тебе есть особая энергетика..." - введение
2. Описание харизмы и естественности
3. Детальное описание - кожа, её сияние, текстура
4. Волосы, их красота и ухоженность
5. Движения, грация, манера держаться

Стиль: восхищение, детальность. Минимум 400 слов.""",

        "beauty_style": f"""Напиши развернутую главу о красоте @{username} (4-5 абзацев):

1. "Красота в твоем случае очевидна для всех..." - введение
2. Лицо как произведение искусства - пропорции, гармония
3. Детальное описание: брови, их форма и выразительность
4. Ресницы, их длина и красота, взгляд
5. Кожа, её безупречность и естественное сияние

Стиль: поэтично, восхищенно. Минимум 400 слов.""",

        "mystery": f"""Напиши развернутую главу о загадочности @{username} (4-5 абзацев):

1. "В тебе есть особая загадочность..." - введение
2. Анализ взгляда - его глубина и тайны
3. Предположения о голосе, его тембре и мелодичности
4. Представления о походке, грации движений
5. Заключение о том, что загадка делает ещё привлекательнее

Стиль: интрига, романтика. Минимум 400 слов.""",

        "influence_on_me": f"""Напиши развернутую главу о влиянии @{username} (4-5 абзацев):

1. "Ты изменил мой взгляд на многие вещи..." - введение
2. Новое внимание к деталям - свет, тени, композиция
3. Понимание того, что красота не требует декораций
4. Благодарность за урок искренности
5. Заключение о том, как это повлияло на мировоззрение

Подпись: "{captions[0] if captions else 'твоя подпись'}"

Минимум 400 слов.""",

        "observations": f"""Напиши развернутую главу о наблюдениях за @{username} (4-5 абзацев):

1. "За время наблюдения сделал интересные открытия..." - введение
2. Фотогеничность - отсутствие плохих ракурсов
3. Выразительные руки, их красота и грация
4. Любовь к свету и умение его использовать
5. Осанка, манера держаться, общая элегантность

Стиль: наблюдательность, восхищение. Минимум 400 слов.""",

        "gratitude_wishes": f"""Напиши развернутую заключительную главу благодарности {username} (5-6 абзацев):

1. "{username}, эта книга подходит к концу..." - введение
2. Благодарность за вдохновение и красоту
3. Пожелания продолжать быть собой
4. Пожелания любви, счастья и ярких моментов
5. Благодарность за то, что такие люди существуют
6. "Спасибо за то, что ты есть. Твой поклонник." - заключение

БИО: "{bio if bio else 'особенная натура'}"

Минимум 500 слов."""
    }
    
    # Fallback контент остается тот же
    fallback_content = {
        "meeting": f"Дорогой {username}, листая Instagram, я случайно наткнулся на твой профиль. Что-то в твоем взгляде заставило остановиться и изучать каждое фото внимательнее. Возможно, это была искренность, которой так не хватает в мире фильтров. Ты показался мне особенным человеком.",
        
        "first_impression": f"Первое, что поразило в твоем профиле - это естественность. Каждое фото рассказывает историю, а твои глаза особенно выразительны. В них читается ум, доброта и глубина души. Твоя улыбка освещает все вокруг - не наигранная, а настоящая.",
        
        "world_view": f"Больше всего поражает то, как ты видишь мир вокруг себя. У тебя есть дар находить прекрасное в обыденном. Твоя внешность отражает внутренний мир - ты красив естественной красотой, которая не нуждается в прикрасах.",
        
        "memorable_moments": f"Есть кадры, которые врезались в память навсегда. Твоя красота живая, меняющаяся. Твои глаза - отдельная поэма, глубокие и выразительные. Когда ты радуешься, они сияют особым светом. Искренность - твое главное качество.",
        
        "energy": f"В тебе есть особая энергетика, которая чувствуется даже через экран телефона. Умеешь быть собой в любой ситуации. У тебя красивая кожа - здоровая, сияющая. Твои движения полны грации и естественности.",
        
        "beauty_style": f"Красота в твоем случае очевидна для всех. Твое лицо - произведение искусства с правильными пропорциями. У тебя красивые брови, длинные ресницы, безупречная кожа с естественным сиянием.",
        
        "mystery": f"В тебе есть особая загадочность, которая не дает покоя. Каждый кадр открывает что-то новое. Твой взгляд загадочен, в нем есть глубина океана. Должно быть, у тебя красивый голос и грациозная походка.",
        
        "influence_on_me": f"Ты изменил мой взгляд на многие вещи. Стал больше внимания обращать на детали вокруг - игру света, выражения лиц. Ты показал, что красота не требует дорогих декораций. Благодаря тебе понял ценность искренности.",
        
        "observations": f"За время наблюдения сделал интересные открытия. Твое лицо очень фотогеничное, у тебя нет плохих ракурсов. Выразительные руки, которые рассказывают истории. Любишь свет и умело его используешь.",
        
        "gratitude_wishes": f"{username}, эта книга подходит к концу, но восхищение остается навсегда. Продолжай быть собой, продолжай фотографировать мир таким, каким ты его видишь. Желаю тебе любви, счастья и ярких моментов. Спасибо за то, что ты есть. Твой поклонник."
    }
    
    # Качественная генерация с увеличенными параметрами
    try:
        prompt = detailed_prompts.get(chapter_type, f"Напиши развернуто и романтично о {chapter_type.replace('_', ' ')}.")
        result = generate_text(prompt, max_tokens=1200, temperature=0.8)  # Увеличиваем для качественных текстов
        
        # Проверяем качество результата
        if len(result.strip()) < 200:  # Если слишком короткий ответ
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
