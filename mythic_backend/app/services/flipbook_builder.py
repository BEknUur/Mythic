# app/services/flipbook_builder.py
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import markdown

# Импортируем новый асинхронный клиент
from app.services.llm_client import generate_flipbook_json

# Подключаем шаблоны из папки app/templates
env = Environment(loader=FileSystemLoader('app/templates'))

async def generate_flipbook_data(run_id: str, image_paths: list[str]) -> dict:
    """
    Главная функция: получает JSON от LLM и возвращает его в виде словаря.
    """
    print("📚 Запрашиваю данные для флипбука у LLM...")
    
    if not image_paths:
        print("⚠️ Нет изображений для генерации флипбука.")
        return {}

    # Вызываем новую функцию с function calling
    flipbook_content = await generate_flipbook_json(image_paths)

    if not flipbook_content or "pages" not in flipbook_content:
        print("❌ Не удалось получить корректные данные от LLM.")
        return {}

    # Преобразуем markdown в HTML для всех текстов
    if "prologue" in flipbook_content:
        flipbook_content["prologue"] = markdown.markdown(flipbook_content["prologue"])
    
    for page in flipbook_content.get("pages", []):
        if "text" in page:
            page["text"] = markdown.markdown(page["text"])

    print("✅ Данные для флипбука успешно сгенерированы и обработаны.")
    return flipbook_content


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
        run_id=run_id,
        prologue=data.get("prologue", "Ваша история начинается здесь..."),
        pages=data.get("pages", [])
    )
    
    out = Path('data') / run_id / 'book.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f"✅ Flipbook HTML создан: {out}") 