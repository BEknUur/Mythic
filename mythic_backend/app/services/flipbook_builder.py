# app/services/flipbook_builder.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import markdown

# подключаем шаблоны из папки app/templates
env = Environment(loader=FileSystemLoader('app/templates'))

def generate_pages_html(run_id: str, image_paths: list[str], comments: list[str]) -> list[str]:
    pages = []

    # ---- обложка ----
    pages.append("""
      <div class="cover-page">
        <h1>Романтическая История</h1>
        <p><i>С любовью...</i></p>
      </div>
    """)

    # ---- каждая картинка + подпись ----
    for idx, img_path in enumerate(image_paths):
        fn = Path(img_path).name
        # теперь URL отдаётся через /data
        pages.append(f"""
          <div class="page-image">
            <img src="/data/{run_id}/images/{fn}" alt="Image {idx+1}" />
          </div>
        """)

        # если есть подпись к этой картинке
        if idx < len(comments):
            html_txt = markdown.markdown(comments[idx])
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