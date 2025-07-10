# app/services/flipbook_builder.py
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import markdown
import re
import base64

# Импортируем асинхронный клиент и настройки из llm_client
from app.services.llm_client import async_client, settings

# Подключаем шаблоны из папки app/templates
env = Environment(loader=FileSystemLoader('app/templates'))

def _get_profile_context(run_id: str) -> dict:
    """Загружает и парсит posts.json для получения контекста о профиле."""
    posts_path = Path('data') / run_id / 'posts.json'
    if not posts_path.exists():
        print(f"⚠️ posts.json не найден для {run_id}")
        return {}

    try:
        posts_data = json.loads(posts_path.read_text(encoding='utf-8'))
        if not posts_data:
            return {}

        # Извлекаем данные из профиля (обычно первый элемент в списке)
        profile = posts_data[0]
        return {
            "username": profile.get("username", "Неизвестный"),
            "full_name": profile.get("fullName", ""),
            "bio": profile.get("biography", ""),
            "captions": [p.get('caption', '') for p in profile.get('latestPosts', [])[:5] if p.get('caption')]
        }
    except (json.JSONDecodeError, IndexError) as e:
        print(f"❌ Ошибка парсинга posts.json для {run_id}: {e}")
        return {}


async def _generate_book_content_from_llm(image_names: list[str], context: dict) -> list[dict]:
    """
    Генерирует контент для книги (заголовки, текст, подписи) с помощью LLM.
    Возвращает список словарей, где каждый словарь представляет страницу.
    """
    system_prompt = f"""
Ты — талантливый писатель-новеллист и поэт. Твоя задача — создать глубокое и эмоциональное литературное произведение, посвященное конкретному человеку, на основе его фотографий и данных из профиля.

**Информация о человеке, которому посвящена книга:**
- **Имя:** {context.get('full_name') or context.get('username')}
- **Никнейм:** @{context.get('username')}
- **Описание профиля (bio):** {context.get('bio', '...')}
- **Примеры его/ее мыслей (подписи к фото):** {json.dumps(context.get('captions', []), ensure_ascii=False)}

Твоя задача — для каждого изображения из списка написать мини-новеллу. Обращайся к человеку лично, на "ты". Используй предоставленную информацию, чтобы текст был максимально персональным.

**Для каждого снимка придумай:**
- **Заголовок (5–8 слов):** Краткий, интригующий и поэтичный.
- **Развёрнутое описание в прозе (минимум 400-600 слов):** Это должен быть полноценный рассказ с деталями, эмоциями, возможно, внутренними монологами или диалогами, и красивыми метафорами. Это настоящая новелла, а не просто описание.
- **Короткую, но ёмкую подпись под фото (10–15 слов):** Она должна дополнять, а не повторять основной текст.

Крайне важно вернуть результат в виде JSON-объекта, содержащего массив `pages`. Никакого лишнего текста, только JSON.
Каждый объект в массиве должен иметь следующую структуру:
{{"title": "...", "text": "...", "image": "...", "caption": "..."}}
    """.strip()

    user_prompt = f"""
Создай литературное произведение на основе этих изображений: {json.dumps(image_names)}.
Убедись, что для каждого изображения есть соответствующий объект в JSON-массиве.
Количество объектов в итоговом JSON-массиве `pages` должно быть равно {len(image_names)}.
    """.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    print("📚 Отправляю развернутый запрос к LLM для генерации новелл...")
    resp = await async_client.chat.completions.create(
        model=settings.AZURE_OPENAI_GPT4_DEPLOYMENT,
        messages=messages,
        temperature=0.8,
        max_tokens=4000, # Увеличиваем лимит для получения длинных текстов
        response_format={"type": "json_object"} # Просим JSON в ответе
    )

    raw_content = resp.choices[0].message.content.strip()
    print("✅ Получен ответ от LLM.")

    try:
        # LLM может вернуть JSON-объект с ключом, например, "pages" или "book"
        data = json.loads(raw_content)
        # Ищем ключ, который содержит список
        for key in data:
            if isinstance(data[key], list):
                return data[key]
        # Если такого ключа нет, но сам ответ - список
        if isinstance(data, list):
             return data
        raise ValueError("В JSON-ответе от LLM не найден массив страниц.")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Ошибка парсинга JSON от LLM: {e}. Ответ:\n{raw_content}")
        # Возвращаем пустой список, чтобы избежать падения
        return []


async def generate_flipbook_data(run_id: str, image_paths: list[str]) -> dict:
    """
    Главная функция: получает JSON от LLM и возвращает его в виде словаря.
    """
    print("📚 Запрашиваю данные для флипбука у LLM...")
    
    if not image_paths:
        print("⚠️ Нет изображений для генерации флипбука.")
        return {}

    # Получаем контекст профиля
    profile_context = _get_profile_context(run_id)
    if not profile_context:
        print("❌ Не удалось получить контекст профиля, генерация будет менее персональной.")

    image_names = [Path(p).name for p in image_paths]
    pages_content = await _generate_book_content_from_llm(image_names, profile_context)

    if not pages_content:
        print("❌ Не удалось получить корректные данные от LLM.")
        return {}
    
    # Сопоставляем абсолютные пути с именами файлов для кодирования
    image_path_map = {Path(p).name: p for p in image_paths}
    
    # Преобразуем markdown в HTML и встраиваем изображения в Base64
    for page in pages_content:
        # Встраиваем изображение
        image_name = page.get("image")
        if image_name in image_path_map:
            try:
                with open(image_path_map[image_name], "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                extension = Path(image_name).suffix.lower().replace('.', '')
                if extension == 'jpg': extension = 'jpeg'
                page["image"] = f"data:image/{extension};base64,{encoded_string}"
            except Exception as e:
                print(f"❌ Ошибка кодирования изображения {image_name}: {e}")
                page["image"] = "" # Пустая строка, если ошибка
        else:
            page["image"] = ""

        if "text" in page:
            page["text"] = markdown.markdown(page["text"])
        if "title" in page:
            # Оборачиваем заголовок, чтобы его можно было стилизовать
             page["title"] = markdown.markdown(f"## {page['title']}")


    print("✅ Данные для флипбука успешно сгенерированы и обработаны.")
    # Возвращаем данные в формате, который ожидает build_flipbook_html
    return {"pages": pages_content, "prologue": ""}


def build_flipbook_html(run_id: str, data: dict):
    """
    Рендерит HTML-флипбук на основе готовых данных (пролог и страницы).
    """
    if not data or "pages" not in data:
        print("️️⚠️ Нет данных для сборки HTML флипбука.")
        return

    tpl = env.get_template('flipbook_template.html')
    
    # Прокидываем данные в шаблон
    html = tpl.render(
        run_id=run_id, # run_id больше не нужен для картинок, но может использоваться где-то еще
        prologue=data.get("prologue", ""),
        pages=data.get("pages", [])
    )
    
    out = Path('data') / run_id / 'book.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f"✅ Flipbook HTML создан: {out}") 