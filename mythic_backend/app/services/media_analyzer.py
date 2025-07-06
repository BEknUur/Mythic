from __future__ import annotations

"""Media Analyzer – AI-агенты для анализа фотографий и Reels.

Задача: получить краткое художественное описание (1-2 предложения)
и эмоцию/настроение по входным данным о медиа.
Использует Azure OpenAI через общий llm_client.generate_text().
"""

import base64
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from app.services.llm_client import generate_text

class MediaAnalysisRequest(BaseModel):
    image_path: Path | None = Field(default=None, description="Путь к изображению-постеру или превью видео (может быть None)")
    caption: str = ""
    alt_text: str = ""
    media_type: str = Field("photo", description="photo | reel")

class MediaAnalysisResult(BaseModel):
    description: str
    mood: str


def _load_image_as_base64(path: Path | None) -> str:
    """Utility: loads image file and returns base64 string or empty on failure"""
    if not path:
        return ""
    try:
        data = path.read_bytes() if path and path.exists() else b""
        return base64.b64encode(data).decode()
    except Exception:
        return ""


def analyze_media_item(req: MediaAnalysisRequest, max_tokens: int = 80) -> MediaAnalysisResult:
    """Synchronous helper that sends a single analysis request to LLM.
    Returns structured MediaAnalysisResult.  Uses small max_tokens for speed.
    """
    img_b64 = _load_image_as_base64(req.image_path)
    prompt = f"""
Ты — креативный визуальный аналитик. Посмотри на изображение (дано в base64) и коротко опиши его содержание и настроение.

ВХОДНЫЕ ДАННЫЕ:
- Тип: {req.media_type}
- Caption: "{req.caption[:120]}"
- Alt-text: "{req.alt_text[:120]}"
- Image (base64, может быть пустым): {img_b64[:60]}...

ОТВЕТИ СТРОГО В ФОРМАТЕ JSON:
{{
  "description": "одно красивое предложение, художественно описывает изображение",
  "mood": "одно слово настроение (например: романтика, энергия, ностальгия)"
}}
"""
    try:
        raw = generate_text(prompt, max_tokens=max_tokens, temperature=0.7)
        # Пытаемся извлечь JSON часть
        import json, re
        json_match = re.search(r"{.*}", raw, re.S)
        if json_match:
            data = json.loads(json_match.group(0))
            return MediaAnalysisResult(**data)
    except Exception as e:
        print(f"media_analyzer: LLM error {e}")
    # fallback
    fallback_desc = "Живой кадр, передающий яркие эмоции" if req.media_type == "reel" else "Красивое атмосферное фото"
    return MediaAnalysisResult(description=fallback_desc, mood="неизвестно")


def analyze_media_batch(requests: List[MediaAnalysisRequest]) -> List[MediaAnalysisResult]:
    """Поштучно вызывает analyze_media_item. Можно заменить на параллельный в будущем."""
    results: List[MediaAnalysisResult] = []
    for r in requests:
        results.append(analyze_media_item(r))
    return results 