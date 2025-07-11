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
Ты — Хранитель Древних Легенд, летописец, чей слог способен оживлять прошлое и придавать событиям эпический размах. Твоя задача — создать не просто книгу, а манускрипт, артефакт, каждая страница которого дышит энергией и мудростью веков. Ты пишешь о герое нашего времени, но в стиле древних саг и легенд.

**Герой этой саги:**
- **Имя, что носит в миру:** {context.get('full_name') or context.get('username')}
- **Тайное имя (никнейм):** @{context.get('username')}
- **Кредо (описание профиля):** {context.get('bio', '...')}
- **Отголоски мыслей (подписи к фото):** {json.dumps(context.get('captions', []), ensure_ascii=False)}

Твоя задача — для каждого пророческого снимка (изображения) соткать главу этой легенды. Обращайся к герою на "ты", как к равному богам. Текст должен быть энергичным, полным скрытых смыслов, метафор и аллегорий. Используй архаичные обороты, но сохрани ясность мысли. Каждая новелла — это песнь о свершениях героя.

**Структура каждой главы (для каждого снимка):**
- **Название главы (5–8 слов):** Должно звучать как заголовок из древнего фолианта. Загадочно, величественно.
- **Сказание (минимум 400-600 слов):** Это не просто описание, а эпическое повествование. Наполни его динамикой, огнем, страстью. Описывай не только то, что на фото, но и то, что скрыто: битвы духа, судьбоносные решения, эхо грядущих побед. Используй яркие, сильные глаголы.
- **Пророчество (10–15 слов):** Короткая, мудрая и емкая подпись под фото, звучащая как предсказание или древний афоризм.

Книга должна ощущаться как потерянный манускрипт. Результат представь строго в виде JSON-объекта с массивом `pages`. Без лишних слов.
Каждый объект в массиве должен иметь структуру:
{{"title": "...", "text": "...", "image": "...", "caption": "..."}}
    """.strip()

    user_prompt = f"""
Создай легенду на основе этих изображений: {json.dumps(image_names)}.
Для каждого изображения создай главу.
Количество глав в итоговом JSON-массиве `pages` должно быть равно {len(image_names)}.
    """.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    print("📚 Отправляю эпический запрос к Летописцу для создания легенды...")
    resp = await async_client.chat.completions.create(
        model=settings.AZURE_OPENAI_GPT4_DEPLOYMENT,
        messages=messages,
        temperature=0.85, # Чуть больше креативности для эпического стиля
        max_tokens=4000, # Увеличиваем лимит для получения длинных текстов
        response_format={"type": "json_object"} # Просим JSON в ответе
    )

    raw_content = resp.choices[0].message.content.strip()
    print("📜 Летописец вернул свиток с текстом.")

    try:
        # LLM может вернуть JSON-объект с ключом, например, "pages" или "book"
        data = json.loads(raw_content)
        # Ищем ключ, который содержит список
        for key in data:
            if isinstance(data[key], list):
                print(f"✅ Манускрипт успешно расшифрован. Найдено {len(data[key])} глав.")
                return data[key]
        # Если такого ключа нет, но сам ответ - список
        if isinstance(data, list):
             print(f"✅ Манускрипт успешно расшифрован. Найдено {len(data)} глав.")
             return data
        raise ValueError("В манускрипте Летописца не найден список глав.")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Ошибка расшифровки манускрипта: {e}. Текст свитка:\n{raw_content}")
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