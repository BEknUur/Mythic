# app/main.py
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import asyncio
from app.services.image_processor import process_folder
from app.services.text_collector import collect_texts
from app.services.book_builder import build_romantic_book, create_pdf_from_html
from app.auth import get_current_user, get_optional_current_user, get_user_from_request
from pydantic import AnyUrl, BaseModel
from pathlib import Path
import json, logging, anyio, random, datetime, uuid, shutil

from app.config import settings
from app.services.apify_client import run_actor, fetch_run, fetch_items
from app.services.downloader import download_photos
from app.auth import clerk_auth

log = logging.getLogger("api")
app = FastAPI(title="Романтическая Летопись Любви", description="Создает красивые романтические книги на основе Instagram профилей для ваших любимых")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",  
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health_check():
    """Простая проверка работы API"""
    return {"status": "ok", "message": "API работает! 💕"}

# ───────────── /start-scrape ────────────────────────────────
@app.get("/start-scrape")
async def start_scrape(url: AnyUrl, current_user: dict = Depends(get_current_user)):
    """Начать скрапинг Instagram профиля - только для авторизованных пользователей"""
    clean_url = str(url).rstrip("/")        

    run_input = {
        "directUrls":     [clean_url],
        "resultsType":    "details",
        "scrapeComments": False,
        
        "resultsLimit":   200,
    }

    webhook = {
        "eventTypes": ["ACTOR.RUN.SUCCEEDED"],
        "requestUrl": f"{settings.BACKEND_BASE}/webhook/apify",
        "payloadTemplate": (
            '{"runId":"{{runId}}",'
            '"datasetId":"{{defaultDatasetId}}"}'
        ),
    }

    run = await run_actor(run_input, webhooks=[webhook])
    run_id = run["id"]
    user_id = current_user.get("sub")
    
    # Сохраняем информацию о пользователе для этого run_id
    run_dir = Path("data") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    user_meta = {"user_id": user_id, "created_at": datetime.datetime.now().isoformat()}
    (run_dir / "user_meta.json").write_text(json.dumps(user_meta, ensure_ascii=False), encoding="utf-8")
    
    log.info("Actor started runId=%s for user=%s", run_id, user_id)
    return {"runId": run_id, "message": "Начинаю исследовать вашу личность... Это займет несколько минут"}


@app.post("/webhook/apify")
async def apify_webhook(request: Request, background: BackgroundTasks):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    run_id = payload.get("runId") or request.headers.get("x-apify-run-id")
    if not run_id:
        raise HTTPException(400, "runId missing")

    dataset_id = payload.get("datasetId")
    if not dataset_id:
        run = await fetch_run(run_id)
        dataset_id = run.get("defaultDatasetId")         

    if not dataset_id:
        raise HTTPException(500, "datasetId unresolved")

    items = await fetch_items(dataset_id)
    run_dir = Path("data") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "posts.json").write_text(json.dumps(items, ensure_ascii=False, indent=2))

    # Получаем user_id из метаданных
    user_id = None
    user_meta_file = run_dir / "user_meta.json"
    if user_meta_file.exists():
        try:
            user_meta = json.loads(user_meta_file.read_text(encoding="utf-8"))
            user_id = user_meta.get("user_id")
        except:
            pass

    # --- качаем картинки ---------------------------------------------------------------
    images_dir = run_dir / "images"
    background.add_task(download_photos, items, images_dir)

    async def _build():
        print("💕 Ожидаем завершения загрузки изображений...")
        await asyncio.sleep(5)
        
        # Проверяем загрузку изображений несколько раз
        for attempt in range(10):
            if images_dir.exists() and any(images_dir.glob("*")):
                print(f"📸 Найдены изображения в папке {images_dir}")
                break
            print(f"⏳ Попытка {attempt + 1}/10: ждем загрузки изображений...")
            await asyncio.sleep(2)

        imgs      = await process_folder(images_dir)
        comments  = collect_texts(run_dir / "posts.json")
        
        # Получаем user_id из метаданных или из текущего пользователя
        user_id = current_user.get("sub")
        user_meta_file = run_dir / "user_meta.json"
        if user_meta_file.exists():
            try:
                user_meta = json.loads(user_meta_file.read_text(encoding="utf-8"))
                user_id = user_meta.get("user_id", user_id)
            except:
                pass
        
        build_romantic_book(run_id, imgs, comments, user_id=user_id)

    background.add_task(lambda: anyio.run(_build))

    return {"status": "processing", "runId": run_id, "message": "Собираю данные, чтобы понять вашу душу... Скоро начну создавать книгу"}


@app.get("/status/{run_id}")
def status(run_id: str, current_user: dict = Depends(get_current_user)):
    """Проверить статус создания книги - только для авторизованных пользователей"""
    run_dir = Path("data") / run_id
    posts_json = run_dir / "posts.json"
    images_dir = run_dir / "images"
    html_file = run_dir / "book.html"
    pdf_file = run_dir / "book.pdf"
    
    log.info(f"Status check for {run_id} by user {current_user.get('sub')}")
    
    data_collected = posts_json.exists()
    images_downloaded = images_dir.exists() and any(images_dir.glob("*"))
    book_generated = html_file.exists()

    message = "Начинаю путешествие по вашему профилю..."

    if book_generated:
        message = "Твоя персональная книга готова! Читай с удовольствием"
    elif images_downloaded:
        romantic_generation_messages = [
            "Пишу историю нашего знакомства — как твоя фотография остановила меня среди тысяч других...",
            "Описываю впечатления от твоих фото — каждое рассказывает отдельную историю...",
            "Делюсь наблюдениями о твоих видео — там столько жизни и энергии...",
            "Создаю главу об особенных моментах — тех, что врезались в память...",
            "Пишу финальные пожелания — слова, которые хотел сказать лично...",
            "Анализирую композицию твоих кадров — ты видишь мир по-особенному...",
            "Изучаю детали в каждом фото — твой взгляд, улыбку, настроение...",
            "Собираю самые искренние слова для твоей персональной книги...",
            "Добавляю последние штрихи — чтобы каждая страница была идеальной...",
            "Создаю подарок, который останется с тобой навсегда..."
        ]
        message = random.choice(romantic_generation_messages)
    elif data_collected:
        # Более личные сообщения об изучении
        analysis_messages = [
            "Изучаю твои фотографии как исследователь — каждая деталь важна...",
            "Рассматриваю твои видео — пытаюсь понять твой характер через движения...",
            "Анализирую места, где ты бываешь — они многое говорят о человеке...", 
            "Читаю твои подписи к фото — в них чувствуется твоя душа...",
            "Изучаю твой стиль — как ты выбираешь ракурсы и моменты...",
            "Собираю пазл твоей личности из сотен маленьких деталей...",
            "Анализирую энергетику в каждом кадре — ты излучаешь особый свет...",
            "Изучаю тонкости — как ты смотришь, улыбаешься, позируешь...",
            "Готовлю материал для книги — каждая страница будет уникальной...",
            "Создаю концепцию твоей истории — она достойна красивых слов..."
        ]
        message = random.choice(analysis_messages)
    
    status_info = {
        "runId": run_id,
        "message": message,
        "stages": {
            "data_collected": data_collected,
            "images_downloaded": images_downloaded,
            "book_generated": book_generated
        },
        "files": {}
    }
    
    if html_file.exists():
        status_info["files"]["html"] = f"/view/{run_id}/book.html"
    
    if pdf_file.exists():
        status_info["files"]["pdf"] = f"/download/{run_id}/book.pdf"
    
    # Добавляем информацию о профиле если есть
    if posts_json.exists():
        try:
            posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
            if posts_data:
                profile = posts_data[0]
                status_info["profile"] = {
                    "username": profile.get("username"),
                    "fullName": profile.get("fullName"),
                    "followers": profile.get("followersCount"),
                    "posts": len(profile.get("latestPosts", []))
                }
        except:
            pass
    
    log.info(f"Status response: {status_info}")
    return status_info


# ───────────── /download/{run_id}/{filename} ─────────────
@app.get("/download/{run_id}/{filename}")
def download_file(run_id: str, filename: str, request: Request):
    """Скачивание готовых файлов (PDF, HTML) - только для авторизованных пользователей"""
    # Проверяем аутентификацию из любого источника
    current_user = get_user_from_request(request)
    if not current_user:
        raise HTTPException(401, "Необходима авторизация для скачивания файлов")
    
    run_dir = Path("data") / run_id
    file_path = run_dir / filename
    
    if not file_path.exists():
        raise HTTPException(404, f"Файл {filename} не найден")
    
    log.info(f"File download {filename} for run {run_id} by user {current_user.get('sub')}")
    
    # Определяем MIME тип
    media_type = "application/pdf" if filename.endswith(".pdf") else "text/html"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


@app.get("/view/{run_id}/book.html")
def view_book_html(run_id: str, request: Request):
    """Просмотр HTML книги - только для авторизованных пользователей"""
    # Проверяем аутентификацию из любого источника
    current_user = get_user_from_request(request)
    if not current_user:
        raise HTTPException(401, "Необходима авторизация для просмотра книги")
    
    run_dir = Path("data") / run_id
    html_file = run_dir / "book.html"
    
    if not html_file.exists():
        raise HTTPException(404, "Книга не найдена")
    
    log.info(f"Book view for run {run_id} by user {current_user.get('sub')}")
    
    html_content = html_file.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)


@app.post("/generate-pdf/{run_id}")
async def generate_pdf(run_id: str, current_user: dict = Depends(get_current_user)):
    """Генерация PDF из HTML книги - только для авторизованных пользователей"""
    run_dir = Path("data") / run_id
    html_file = run_dir / "book.html"
    pdf_file = run_dir / "book.pdf"
    
    if not html_file.exists():
        raise HTTPException(404, "HTML книга не найдена")
    
    if pdf_file.exists():
        return {"status": "exists", "message": "PDF уже создан", "download_url": f"/download/{run_id}/book.pdf"}
    
    log.info(f"PDF generation for run {run_id} by user {current_user.get('sub')}")
    
    try:
        await create_pdf_from_html(str(html_file), str(pdf_file))
        return {"status": "success", "message": "PDF создан", "download_url": f"/download/{run_id}/book.pdf"}
    except Exception as e:
        log.error(f"Error creating PDF: {e}")
        raise HTTPException(500, f"Ошибка создания PDF: {e}")


# ───────────── / (главная страница) ─────────────────────
@app.get("/")
def home():
    """Главная страница с веб-интерфейсом"""
    static_dir = Path("static")
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        html_content = index_file.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    else:
        return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Романтическая Летопись Любви</title>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            min-height: 100vh;
            padding: 0;
            display: flex;
        }
        
        /* Sidebar Styles - Shadcn inspired */
        .sidebar {
            width: 280px;
            background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
            border-right: 1px solid #2a2a2a;
            padding: 0;
            display: flex;
            flex-direction: column;
            position: fixed;
            left: 0;
            top: 0;
            height: 100vh;
            z-index: 1000;
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .sidebar-header {
            padding: 24px 20px;
            border-bottom: 1px solid #2a2a2a;
        }
        
        .sidebar-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #ffffff;
            text-decoration: none;
        }
        
        .sidebar-logo-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #ff6b6b 0%, #f368e0 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        
        .sidebar-logo-text {
            font-family: 'Dancing Script', cursive;
            font-size: 20px;
            font-weight: 700;
        }
        
        .sidebar-nav {
            flex: 1;
            padding: 20px 0;
        }
        
        .nav-section {
            margin-bottom: 32px;
        }
        
        .nav-section-title {
            color: #888888;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            padding: 0 20px 12px;
            border-bottom: 1px solid #2a2a2a;
            margin-bottom: 16px;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            color: #cccccc;
            text-decoration: none;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            margin: 2px 8px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .nav-item::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 0;
            background: linear-gradient(135deg, #ff6b6b 0%, #f368e0 100%);
            border-radius: 8px 0 0 8px;
            transition: width 0.2s ease;
        }
        
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.05);
            color: #ffffff;
            transform: translateX(4px);
        }
        
        .nav-item:hover::before {
            width: 3px;
        }
        
        .nav-item.active {
            background: rgba(255, 107, 107, 0.1);
            color: #ff6b6b;
        }
        
        .nav-item.active::before {
            width: 3px;
        }
        
        .nav-icon {
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        
        .nav-text {
            flex: 1;
        }
        
        .nav-badge {
            background: #ff6b6b;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            font-weight: 600;
        }
        
        .sidebar-footer {
            padding: 20px;
            border-top: 1px solid #2a2a2a;
        }
        
        .progress-section {
            margin-bottom: 16px;
        }
        
        .progress-title {
            color: #cccccc;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .progress-bar-container {
            background: #2a2a2a;
            border-radius: 4px;
            height: 6px;
            overflow: hidden;
        }
        
        .progress-bar-fill {
            background: linear-gradient(135deg, #ff6b6b 0%, #f368e0 100%);
            height: 100%;
            width: 65%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            color: #888888;
            font-size: 11px;
            margin-top: 4px;
        }
        
        .sidebar-toggle {
            position: fixed;
            top: 24px;
            left: 300px;
            z-index: 1001;
            background: rgba(0, 0, 0, 0.8);
            border: none;
            border-radius: 8px;
            padding: 8px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .sidebar-toggle:hover {
            background: rgba(0, 0, 0, 0.9);
            transform: scale(1.1);
        }
        
        .main-content {
            flex: 1;
            margin-left: 280px;
            padding: 20px;
            transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .sidebar.collapsed {
            transform: translateX(-280px);
        }
        
        .sidebar.collapsed + .sidebar-toggle {
            left: 20px;
        }
        
        .main-content.expanded {
            margin-left: 0;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-280px);
            }
            
            .sidebar.mobile-open {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
            }
            
            .sidebar-toggle {
                left: 20px;
            }
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
            padding: 60px 40px;
            text-align: center;
            color: white;
            position: relative;
        }
        
        .header::before {
            content: "💕";
            position: absolute;
            top: 20px;
            left: 40px;
            font-size: 2em;
            animation: float 3s ease-in-out infinite;
        }
        
        .header::after {
            content: "💖";
            position: absolute;
            top: 30px;
            right: 40px;
            font-size: 1.5em;
            animation: float 3s ease-in-out infinite reverse;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .main-title {
            font-family: 'Dancing Script', cursive;
            font-size: 4em;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .subtitle {
            font-family: 'Playfair Display', serif;
            font-size: 1.6em;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        
        .heart-decoration {
            font-size: 2.5em;
            animation: heartbeat 2s ease-in-out infinite;
        }
        
        @keyframes heartbeat {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .content {
            padding: 60px 40px;
        }
        
        .love-form {
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .form-title {
            font-family: 'Dancing Script', cursive;
            font-size: 2.5em;
            color: #d63031;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        .input-label {
            display: block;
            font-weight: 600;
            color: #2d3436;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .input-field {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #fdcb6e;
            border-radius: 12px;
            font-size: 1em;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }
        
        .input-field:focus {
            outline: none;
            border-color: #e17055;
            box-shadow: 0 0 0 3px rgba(225, 112, 85, 0.2);
        }
        
        .love-button {
            width: 100%;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 30%, #ff9ff3 70%, #f368e0 100%);
            background-size: 300% 300%;
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-family: 'Inter', sans-serif;
            margin-top: 20px;
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
            animation: gradientShift 6s ease infinite;
        }
        
        .love-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.5s;
        }
        
        .love-button:hover::before {
            left: 100%;
        }
        
        .love-button:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 15px 45px rgba(255, 107, 107, 0.4);
            background-position: 100% 0;
        }
        
        .love-button:active {
            transform: translateY(-1px) scale(0.98);
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .feature-card {
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 107, 107, 0.05), transparent);
            transition: left 0.8s ease;
        }
        
        .feature-card:hover::before {
            left: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 60px rgba(255, 107, 107, 0.15);
            background: linear-gradient(135deg, #ffffff 0%, #fff5f5 100%);
        }
        
        .feature-icon {
            font-size: 3.5em;
            margin-bottom: 20px;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            display: inline-block;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
        }
        
        .feature-card:hover .feature-icon {
            transform: scale(1.2) rotate(5deg);
            filter: drop-shadow(0 8px 16px rgba(255, 107, 107, 0.3));
        }
        
        .feature-title {
            font-family: 'Playfair Display', serif;
            font-size: 1.3em;
            color: #2d3436;
            margin-bottom: 15px;
        }
        
        .feature-text {
            color: #636e72;
            line-height: 1.6;
        }
        
        /* Mobile adaptations for main content */
        @media (max-width: 768px) {
            .content {
                padding: 40px 20px;
            }
            
            .header {
                padding: 40px 20px;
            }
            
            .main-title {
                font-size: 2.5em;
            }
            
            .love-form {
                padding: 30px 20px;
            }
            
            .features {
                grid-template-columns: 1fr;
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <!-- Sidebar Header -->
        <div class="sidebar-header">
            <a href="/" class="sidebar-logo">
                <div class="sidebar-logo-icon">💕</div>
                <span class="sidebar-logo-text">Mythic</span>
            </a>
        </div>
        
        <!-- Sidebar Navigation -->
        <nav class="sidebar-nav">
            <!-- Main Actions -->
            <div class="nav-section">
                <div class="nav-section-title">Основное</div>
                <a href="#" class="nav-item active" data-action="create-book">
                    <div class="nav-icon">📖</div>
                    <span class="nav-text">Создать книгу</span>
                </a>
                <a href="#" class="nav-item" data-action="book-to-tiktok">
                    <div class="nav-icon">🎬</div>
                    <span class="nav-text">Книга → TikTok</span>
                    <span class="nav-badge">Новое</span>
                </a>
                <a href="#" class="nav-item" data-action="write-fanfic">
                    <div class="nav-icon">✍️</div>
                    <span class="nav-text">Написать фанфик</span>
                </a>
                <a href="#" class="nav-item" data-action="generate-comic">
                    <div class="nav-icon">🎨</div>
                    <span class="nav-text">Сгенерировать комикс</span>
                </a>
            </div>
            
            <!-- Library -->
            <div class="nav-section">
                <div class="nav-section-title">Библиотека</div>
                <a href="#" class="nav-item" data-action="my-books">
                    <div class="nav-icon">📚</div>
                    <span class="nav-text">Мои книги</span>
                </a>
                <a href="#" class="nav-item" data-action="favorites">
                    <div class="nav-icon">⭐</div>
                    <span class="nav-text">Избранное</span>
                </a>
                <a href="#" class="nav-item" data-action="gallery">
                    <div class="nav-icon">🖼️</div>
                    <span class="nav-text">Мини-галерея</span>
                </a>
            </div>
            
            <!-- Settings -->
            <div class="nav-section">
                <div class="nav-section-title">Настройки</div>
                <a href="#" class="nav-item" data-action="settings">
                    <div class="nav-icon">⚙️</div>
                    <span class="nav-text">Настройки</span>
                </a>
                <a href="#" class="nav-item" data-action="help">
                    <div class="nav-icon">❓</div>
                    <span class="nav-text">Помощь</span>
                </a>
            </div>
        </nav>
        
        <!-- Sidebar Footer -->
        <div class="sidebar-footer">
            <div class="progress-section">
                <div class="progress-title">Прогресс чтения</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill"></div>
                </div>
                <div class="progress-text">65% завершено</div>
            </div>
        </div>
    </div>
    
    <!-- Sidebar Toggle Button -->
    <button class="sidebar-toggle" id="sidebarToggle">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
    </button>
    
    <!-- Main Content -->
    <div class="main-content" id="mainContent">
        <div class="container">
            <div class="header">
                <h1 class="main-title">Романтическая Летопись Любви</h1>
                <p class="subtitle">Создайте красивую книгу воспоминаний для вашего любимого человека</p>
                <div class="heart-decoration">💝</div>
            </div>
            
            <div class="content">
                <div class="love-form">
                    <h2 class="form-title">Создать Книгу Любви</h2>
                    <form id="loveBookForm">
                        <div class="input-group">
                            <label class="input-label" for="instagramUrl">Instagram профиль вашего любимого человека</label>
                            <input type="url" id="instagramUrl" class="input-field" placeholder="https://www.instagram.com/username" required>
                        </div>
                        
                        <button type="submit" class="love-button">
                            Создать Романтическую Книгу ❤️    
                        </button>
                    </form>
                </div>
                
                <div class="features">
                    <div class="feature-card">
                        <div class="feature-icon">📖</div>
                        <h3 class="feature-title">Красивая Летопись</h3>
                        <p class="feature-text">Создаем красивую книгу с фотографиями и романтическими текстами о вашем любимом человеке</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">💌</div>
                        <h3 class="feature-title">Романтические Послания</h3>
                        <p class="feature-text">Добавляем трогательные тексты и цитаты о любви между фотографиями</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">🎨</div>
                        <h3 class="feature-title">Элегантный Дизайн</h3>
                        <p class="feature-text">Профессиональное оформление с романтическими цветами и шрифтами</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">📱</div>
                        <h3 class="feature-title">Просто и Быстро</h3>
                        <p class="feature-text">Просто укажите Instagram профиль - мы сделаем всё остальное за вас</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Sidebar toggle functionality
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mainContent = document.getElementById('mainContent');
        
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
        
        // Navigation functionality
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all items
                navItems.forEach(nav => nav.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
                
                // Handle different actions
                const action = item.getAttribute('data-action');
                handleNavigation(action);
            });
        });
        
        function handleNavigation(action) {
            switch(action) {
                case 'create-book':
                    showCreateBookForm();
                    break;
                case 'book-to-tiktok':
                    showBookToTikTok();
                    break;
                case 'write-fanfic':
                    showFanficForm();
                    break;
                case 'generate-comic':
                    showComicGenerator();
                    break;
                case 'my-books':
                    showMyBooks();
                    break;
                case 'favorites':
                    showFavorites();
                    break;
                case 'gallery':
                    showGallery();
                    break;
                case 'settings':
                    showSettings();
                    break;
                case 'help':
                    showHelp();
                    break;
                default:
                    console.log('Unknown action:', action);
            }
        }
        
        function showCreateBookForm() {
            // Default view is already the create book form
            console.log('Showing create book form');
        }
        
        function showBookToTikTok() {
            alert('🎬 Функция "Книга → TikTok" скоро будет доступна!\n\nМы работаем над созданием коротких видео из ваших романтических книг для TikTok и Instagram.');
        }
        
        function showFanficForm() {
            alert('✍️ Функция "Написать фанфик" скоро будет доступна!\n\nВы сможете создавать уникальные фанфики на основе фотографий и данных профиля.');
        }
        
        function showComicGenerator() {
            alert('🎨 Функция "Сгенерировать комикс" скоро будет доступна!\n\nМы создадим комиксы из ключевых моментов вашей истории любви.');
        }
        
        function showMyBooks() {
            alert('📚 Функция "Мои книги" скоро будет доступна!\n\nЗдесь будут храниться все ваши созданные книги.');
        }
        
        function showFavorites() {
            alert('⭐ Функция "Избранное" скоро будет доступна!\n\nСохраняйте лучшие моменты и страницы из ваших книг.');
        }
        
        function showGallery() {
            alert('🖼️ Функция "Мини-галерея" скоро будет доступна!\n\nБыстрый просмотр всех изображений из ваших проектов.');
        }
        
        function showSettings() {
            alert('⚙️ Функция "Настройки" скоро будет доступна!\n\nНастройте стиль книг, языки и персонализацию.');
        }
        
        function showHelp() {
            alert('❓ Нужна помощь?\n\n• Введите Instagram URL\n• Нажмите "Создать книгу"\n• Дождитесь обработки\n• Скачайте готовую книгу\n\nПо вопросам: support@mythic.love');
        }
        
        // Form submission
        document.getElementById('loveBookForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = document.getElementById('instagramUrl').value;
            const button = document.querySelector('.love-button');
            
            button.disabled = true;
            button.innerHTML = 'Создаем книгу... 💕';
            
            try {
                const response = await fetch(`/start-scrape?url=${encodeURIComponent(url)}`);
                const result = await response.json();
                
                if (response.ok) {
                    // Перенаправляем на страницу статуса
                    window.location.href = `/status-page?runId=${result.runId}`;
                } else {
                    throw new Error(result.message || 'Произошла ошибка');
                }
            } catch (error) {
                alert('Ошибка: ' + error.message);
                button.disabled = false;
                button.innerHTML = 'Создать Романтическую Книгу ❤️';
            }   
        });
        
        // Progress animation
        function animateProgress() {
            const progressFill = document.querySelector('.progress-bar-fill');
            const progressText = document.querySelector('.progress-text');
            
            let progress = 65;
            const interval = setInterval(() => {
                progress += Math.random() * 2;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    progressText.textContent = 'Готово!';
                } else {
                    progressText.textContent = `${Math.floor(progress)}% завершено`;
                }
                progressFill.style.width = `${progress}%`;
            }, 2000);
        }
        
        // Mobile responsive
        function handleMobileMenu() {
            if (window.innerWidth <= 768) {
                sidebar.classList.add('mobile-menu');
                
                sidebarToggle.addEventListener('click', () => {
                    sidebar.classList.toggle('mobile-open');
                });
                
                // Close sidebar when clicking outside
                document.addEventListener('click', (e) => {
                    if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                        sidebar.classList.remove('mobile-open');
                    }
                });
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            handleMobileMenu();
            // animateProgress(); // Uncomment if you want animated progress
        });
        
        window.addEventListener('resize', handleMobileMenu);
    </script>
</body>
</html>
        """)

# ───────────── /status-page ─────────────────────
@app.get("/status-page")
def status_page(runId: str):
    """Страница отслеживания статуса создания книги"""
    
    # JavaScript код как отдельная строка для избежания конфликтов с f-string
    js_code = """
        const runId = '""" + runId + """';
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const resultContainer = document.getElementById('resultContainer');
        const downloadButtons = document.getElementById('downloadButtons');
        
        const stages = [
            { text: 'Изучаю твои фотографии с особым вниманием...', progress: 20 },
            { text: 'Рассматриваю твои видео — столько энергии в них...', progress: 40 },
            { text: 'Пишу личные слова специально для тебя...', progress: 60 },
            { text: 'Добавляю романтические штрихи в твою книгу...', progress: 80 },
            { text: 'Создаю финальную версию твоего подарка...', progress: 95 }
        ];
        
        let currentStage = 0;
        
        // Функция анимации печатающейся машинки
        function typewriterAnimation(element, text, speed = 80) {
            return new Promise((resolve) => {
                element.textContent = '';
                let i = 0;
                
                function typeChar() {
                    if (i < text.length) {
                        element.textContent += text.charAt(i);
                        i++;
                        setTimeout(typeChar, speed);
                    } else {
                        resolve();
                    }
                }
                
                typeChar();
            });
        }
        
        async function updateProgress() {
            if (currentStage < stages.length) {
                const stage = stages[currentStage];
                progressFill.style.width = stage.progress + '%';
                
                // Анимируем появление романтического текста
                await typewriterAnimation(progressText, stage.text, 60);
                
                currentStage++;
                setTimeout(updateProgress, 4000); // Увеличил время для просмотра анимации
            }
        }
        
        async function checkStatus() {
            try {
                const response = await fetch(`/status/${runId}`);
                const status = await response.json();
                
                // Не перезаписываем сообщения stages, пока книга не готова
                
                if (status.stages.book_generated) {
                    progressFill.style.width = '100%';
                    progressText.textContent = 'Готово! ✨';
                    
                    setTimeout(() => {
                        document.querySelector('.progress-container').style.display = 'none';
                        document.querySelector('.heart-loading').style.display = 'none';
                        document.querySelector('.status-message').textContent = 'Романтическая книга создана с любовью! 💝';
                        resultContainer.style.display = 'block';
                        
                        if (status.files.html) {
                            const viewBtn = document.createElement('a');
                            viewBtn.href = status.files.html;
                            viewBtn.className = 'download-btn btn-view';
                            viewBtn.textContent = 'Просмотреть книгу 👀';
                            viewBtn.target = '_blank';
                            downloadButtons.appendChild(viewBtn);
                        }
                        
                        if (status.files.pdf) {
                            const downloadBtn = document.createElement('a');
                            downloadBtn.href = status.files.pdf;
                            downloadBtn.className = 'download-btn btn-download';
                            downloadBtn.textContent = 'Скачать PDF 💕';
                            downloadBtn.download = 'romantic_book.pdf';
                            downloadButtons.appendChild(downloadBtn);
                        }
                    }, 1000);
                } else {
                    setTimeout(checkStatus, 3000);
                }
            } catch (error) {
                setTimeout(checkStatus, 5000);
            }
        }
        
        // Запускаем обновление прогресса и проверку статуса
        updateProgress();
        setTimeout(checkStatus, 5000);
    """
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Создание Романтической Книги</title>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .status-container {{
            max-width: 600px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}
        
        .status-title {{
            font-family: 'Dancing Script', cursive;
            font-size: 3em;
            color: #e84393;
            margin-bottom: 30px;
        }}
        
        .status-message {{
            font-size: 1.2em;
            color: #2d3436;
            margin-bottom: 40px;
            line-height: 1.6;
        }}
        
        .progress-container {{
            margin: 40px 0;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 12px;
            background: #ddd;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 6px;
        }}
        
        .progress-text {{
            color: #636e72;
            font-style: italic;
            min-height: 24px;
        }}
        
        .heart-loading {{
            font-size: 4em;
            margin: 30px 0;
            animation: heartbeat 1.5s ease-in-out infinite;
        }}
        
        @keyframes heartbeat {{
            0%, 100% {{ transform: scale(1) rotate(0deg); }}
            50% {{ transform: scale(1.2) rotate(5deg); }}
        }}
        
        .result-container {{
            display: none;
            margin-top: 30px;
        }}
        
        .success-title {{
            font-family: 'Dancing Script', cursive;
            font-size: 2.5em;
            color: #00b894;
            margin-bottom: 20px;
        }}
        
        .download-buttons {{
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 30px;
        }}
        
        .download-btn {{
            padding: 16px 32px;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-size: 14px;
            min-width: 180px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.15);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        .download-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 100%);
            transform: translateX(-100%);
            transition: transform 0.6s ease;
        }}
        
        .download-btn:hover::before {{
            transform: translateX(100%);
        }}
        
        .btn-view {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-view:hover {{
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-download {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .btn-download:hover {{
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 12px 35px rgba(245, 87, 108, 0.4);
        }}
        
        .download-btn:active {{
            transform: translateY(-1px) scale(1.02);
        }}
        
        @media (max-width: 768px) {{
            .status-container {{
                padding: 40px 20px;
            }}
            
            .download-buttons {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="status-container">
        <h1 class="status-title">Создаем Вашу Книгу Любви</h1>
        <p class="status-message">Пожалуйста, подождите... Мы собираем самые красивые моменты и создаем романтическую книгу для вашего любимого человека ❤️</p>
        
        <div class="heart-loading">💕</div>
        
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <p class="progress-text" id="progressText">Собираем фотографии...</p>
        </div>
        
        <div class="result-container" id="resultContainer">
            <h2 class="success-title">Ваша книга готова!</h2>
            <p>Теперь вы можете просмотреть или скачать романтическую книгу</p>
            <div class="download-buttons" id="downloadButtons">
                
            </div>
        </div>
    </div>
    
    <script>
        {js_code}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)

@app.post("/create-book")
async def create_book(request: Request, background: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Создает романтическую книгу на основе данных профиля - только для авторизованных пользователей"""
    try:
        body = await request.json()
        run_id = body.get("runId")
        book_format = body.get("format", "classic")  # "classic" или "zine"
        
        if not run_id:
            raise HTTPException(400, "runId обязателен")
        
        # Проверяем, что данные существуют
        run_dir = Path("data") / run_id
        if not run_dir.exists():
            raise HTTPException(404, f"Данные для runId {run_id} не найдены")
            
        log.info(f"Book creation started for run {run_id} by user {current_user.get('sub')}")
    except Exception as e:
        raise HTTPException(400, f"Ошибка в параметрах запроса: {e}")

    async def _build():
        # Ждем завершения загрузки изображений
        images_dir = run_dir / "images"
        for attempt in range(10):  # Максимум 20 секунд ожидания
            if images_dir.exists() and any(images_dir.glob("*")):
                print(f"📸 Найдены изображения в папке {images_dir}")
                break
            print(f"⏳ Попытка {attempt + 1}/10: ждем загрузки изображений...")
            await asyncio.sleep(2)

        imgs      = await process_folder(images_dir)
        comments  = collect_texts(run_dir / "posts.json")
        
        # Получаем user_id из метаданных или из текущего пользователя
        user_id = current_user.get("sub")
        user_meta_file = run_dir / "user_meta.json"
        if user_meta_file.exists():
            try:
                user_meta = json.loads(user_meta_file.read_text(encoding="utf-8"))
                user_id = user_meta.get("user_id", user_id)
            except:
                pass
        
        build_romantic_book(run_id, imgs, comments, book_format, user_id=user_id)

    background.add_task(lambda: anyio.run(_build))

    format_name = "классическую книгу" if book_format == "classic" else "мозаичный зин"
    return {"status": "processing", "runId": run_id, "format": book_format, "message": f"Создание {format_name} началось! Скоро будет готова"}

# Модели для работы с книгами пользователя
class SaveBookRequest(BaseModel):
    run_id: str
    custom_title: str = None

class UserBook(BaseModel):
    id: str
    run_id: str
    title: str
    created_at: str
    profile_username: str = None
    profile_full_name: str = None
    has_pdf: bool = False
    has_html: bool = False

class UserBooksResponse(BaseModel):
    books: list[UserBook]
    total: int

# Функции для работы с пользовательскими книгами
def get_user_books_db_path(user_id: str) -> Path:
    """Получить путь к файлу с книгами пользователя"""
    user_books_dir = Path("data") / "user_books"
    user_books_dir.mkdir(parents=True, exist_ok=True)
    return user_books_dir / f"{user_id}.json"

def load_user_books(user_id: str) -> list[dict]:
    """Загрузить книги пользователя"""
    books_file = get_user_books_db_path(user_id)
    if not books_file.exists():
        return []
    try:
        return json.loads(books_file.read_text(encoding="utf-8"))
    except:
        return []

def save_user_books(user_id: str, books: list[dict]):
    """Сохранить книги пользователя"""
    books_file = get_user_books_db_path(user_id)
    books_file.write_text(json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8")

def copy_book_to_user_library(run_id: str, user_id: str, book_id: str) -> bool:
    """Копировать файлы книги в библиотеку пользователя"""
    try:
        source_dir = Path("data") / run_id
        user_library_dir = Path("data") / "user_books" / user_id / book_id
        user_library_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем файлы книги
        for file in ["book.html", "book.pdf", "posts.json"]:
            source_file = source_dir / file
            if source_file.exists():
                shutil.copy2(source_file, user_library_dir / file)
        
        # Копируем папку с изображениями
        source_images = source_dir / "images"
        if source_images.exists():
            target_images = user_library_dir / "images"
            if target_images.exists():
                shutil.rmtree(target_images)
            shutil.copytree(source_images, target_images)
        
        return True
    except Exception as e:
        log.error(f"Ошибка копирования книги {run_id} для пользователя {user_id}: {e}")
        return False

# Эндпоинты для управления книгами пользователя

@app.post("/books/save", response_model=dict)
async def save_book_to_library(request: SaveBookRequest, current_user: dict = Depends(get_current_user)):
    """Сохранить книгу в библиотеку пользователя"""
    user_id = current_user.get("sub")
    run_id = request.run_id
    
    # Проверяем, что книга существует и завершена
    run_dir = Path("data") / run_id
    html_file = run_dir / "book.html"
    if not html_file.exists():
        raise HTTPException(404, "Книга не найдена или еще не готова")
    
    # Загружаем данные профиля из posts.json
    posts_json = run_dir / "posts.json"
    profile_username = None
    profile_full_name = None
    if posts_json.exists():
        try:
            posts_data = json.loads(posts_json.read_text(encoding="utf-8"))
            if posts_data:
                profile = posts_data[0]
                profile_username = profile.get("username")
                profile_full_name = profile.get("fullName")
        except:
            pass
    
    # Генерируем уникальный ID для книги
    book_id = str(uuid.uuid4())
    
    # Определяем название книги
    title = request.custom_title or f"Для {profile_full_name or profile_username or 'Неизвестный'} с любовью"
    
    # Загружаем существующие книги пользователя
    books = load_user_books(user_id)
    
    # Проверяем, не сохранена ли уже эта книга
    for book in books:
        if book["run_id"] == run_id:
            return {"success": True, "message": "Книга уже сохранена в вашей библиотеке", "book_id": book["id"]}
    
    # Копируем файлы книги в библиотеку пользователя
    if not copy_book_to_user_library(run_id, user_id, book_id):
        raise HTTPException(500, "Ошибка сохранения книги")
    
    # Добавляем книгу в список
    pdf_file = run_dir / "book.pdf"
    new_book = {
        "id": book_id,
        "run_id": run_id,
        "title": title,
        "created_at": datetime.datetime.now().isoformat(),
        "profile_username": profile_username,
        "profile_full_name": profile_full_name,
        "has_pdf": pdf_file.exists(),
        "has_html": html_file.exists()
    }
    
    books.append(new_book)
    save_user_books(user_id, books)
    
    log.info(f"Книга {run_id} сохранена в библиотеке пользователя {user_id}")
    return {"success": True, "message": "Книга сохранена в вашей библиотеке", "book_id": book_id}

@app.get("/books/my", response_model=UserBooksResponse)
async def get_my_books(current_user: dict = Depends(get_current_user)):
    """Получить список книг пользователя"""
    user_id = current_user.get("sub")
    books_data = load_user_books(user_id)
    
    # Преобразуем в модели Pydantic
    books = [UserBook(**book) for book in books_data]
    
    # Сортируем по дате создания (новые сначала)
    books.sort(key=lambda x: x.created_at, reverse=True)
    
    return UserBooksResponse(books=books, total=len(books))

@app.delete("/books/{book_id}")
async def delete_book(book_id: str, current_user: dict = Depends(get_current_user)):
    """Удалить книгу из библиотеки пользователя"""
    user_id = current_user.get("sub")
    books = load_user_books(user_id)
    
    # Находим книгу
    book_to_delete = None
    for i, book in enumerate(books):
        if book["id"] == book_id:
            book_to_delete = book
            books.pop(i)
            break
    
    if not book_to_delete:
        raise HTTPException(404, "Книга не найдена")
    
    # Удаляем файлы книги
    book_dir = Path("data") / "user_books" / user_id / book_id
    if book_dir.exists():
        try:
            shutil.rmtree(book_dir)
        except Exception as e:
            log.error(f"Ошибка удаления файлов книги {book_id}: {e}")
    
    # Сохраняем обновленный список
    save_user_books(user_id, books)
    
    log.info(f"Книга {book_id} удалена из библиотеки пользователя {user_id}")
    return {"success": True, "message": "Книга удалена из библиотеки"}

@app.get("/books/{book_id}/view")
async def view_saved_book(book_id: str, request: Request):
    """Просмотр сохраненной книги"""
    # Проверяем аутентификацию из любого источника (включая токен из URL)
    current_user = get_user_from_request(request)
    if not current_user:
        raise HTTPException(401, "Необходима авторизация для просмотра книги")
    
    user_id = current_user.get("sub")
    books = load_user_books(user_id)
    
    # Находим книгу
    book = None
    for b in books:
        if b["id"] == book_id:
            book = b
            break
    
    if not book:
        raise HTTPException(404, "Книга не найдена")
    
    # Путь к HTML файлу книги
    book_dir = Path("data") / "user_books" / user_id / book_id
    html_file = book_dir / "book.html"
    
    if not html_file.exists():
        raise HTTPException(404, "HTML файл книги не найден")
    
    log.info(f"Saved book view for book {book_id} by user {user_id}")
    return HTMLResponse(html_file.read_text(encoding="utf-8"))

@app.get("/books/{book_id}/download/{filename}")
async def download_saved_book(book_id: str, filename: str, request: Request):
    """Скачать файл сохраненной книги"""
    # Проверяем аутентификацию из любого источника (включая токен из URL)
    current_user = get_user_from_request(request)
    if not current_user:
        raise HTTPException(401, "Необходима авторизация для скачивания файла")
    
    user_id = current_user.get("sub")
    books = load_user_books(user_id)
    
    # Находим книгу
    book = None
    for b in books:
        if b["id"] == book_id:
            book = b
            break
    
    if not book:
        raise HTTPException(404, "Книга не найдена")
    
    # Путь к файлу
    book_dir = Path("data") / "user_books" / user_id / book_id
    file_path = book_dir / filename
    
    if not file_path.exists():
        raise HTTPException(404, "Файл не найден")
    
    log.info(f"Saved book download {filename} for book {book_id} by user {user_id}")
    
    # Определяем MIME тип
    if filename.endswith('.pdf'):
        media_type = 'application/pdf'
    elif filename.endswith('.html'):
        media_type = 'text/html'
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )
