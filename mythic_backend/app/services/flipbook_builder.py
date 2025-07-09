# app/services/flipbook_builder.py
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import markdown

# подключаем шаблоны из папки app/templates
env = Environment(loader=FileSystemLoader('app/templates'))

def generate_pages_html(run_id: str, image_paths: list[str], text_pages: list[str]) -> list[str]:
    """
    Генерирует HTML-страницы для флипбука, используя переданные тексты.
    """
    print("📚 Собираю страницы для флипбука...")
    
    pages = []

    pages.append("""
      <div class="cover-page">
        <h1>Романтическая История</h1>
        <p><i>С любовью...</i></p>
      </div>
    """)

    for idx, img_path in enumerate(image_paths):
        fn = Path(img_path).name
        pages.append(f"""
          <div class="page-image">
            <img src="/data/{run_id}/images/{fn}" alt="Image {idx+1}" />
          </div>
        """)

        if idx < len(text_pages):
            # Конвертируем Markdown в HTML
            html_txt = markdown.markdown(text_pages[idx])
            pages.append(f"""
              <div class="text-content">
                {html_txt}
              </div>
            """)

    return pages


def build_flipbook_html(run_id: str, pages: list[str]):
    tpl = env.get_template('flipbook_template.html')
    html = tpl.render(pages=pages, run_id=run_id)
    out = Path('data') / run_id / 'book.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f"✅ Flipbook HTML создан: {out}") 