import os
import re
from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import StreamingResponse, Response
from openai import AsyncAzureOpenAI
import json

router = APIRouter(prefix="/api")

# Список запрещенных слов и тем
FORBIDDEN_WORDS = [
    # Добавьте сюда запрещенные слова на русском и английском
    "блядь", "сука", "хуй", "пизда", "ебать", "ебаный", "говно", "дерьмо",
    "fuck", "shit", "bitch", "damn", "ass", "crap"
]

FORBIDDEN_TOPICS = [
    "спорт", "футбол", "хоккей", "баскетбол", "теннис", "олимпиада",
    "погода", "климат", "дождь", "снег", "солнце",
    "политика", "президент", "выборы", "партия", "власть",
    "религия", "бог", "церковь", "молитва", "вера",
    "медицина", "лечение", "болезнь", "врач", "больница",
    "еда", "рецепт", "готовка", "кулинария", "ресторан"
]

def check_content_policy(text: str) -> tuple[bool, str]:
    """
    Проверяет текст на соответствие политике контента.
    Возвращает (is_allowed, reason)
    """
    text_lower = text.lower()
    
    # Проверка на запрещенные слова
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            return False, "Обнаружена недопустимая лексика"
    
    # Проверка на запрещенные темы
    for topic in FORBIDDEN_TOPICS:
        if topic in text_lower:
            return False, f"Обсуждение темы '{topic}' не относится к редактированию текста"
    
    # Проверка на наличие текста для редактирования
    # Если сообщение слишком короткое и не содержит явного текста для редактирования
    if len(text.strip()) < 10 and not any(word in text_lower for word in ["редактировать", "изменить", "улучшить", "исправить"]):
        return False, "Пожалуйста, предоставьте текст для редактирования"
    
    return True, ""

def is_text_editing_request(text: str) -> bool:
    """
    Проверяет, является ли запрос связанным с редактированием текста.
    """
    editing_keywords = [
        "изменить", "улучшить", "исправить", "редактировать", "переписать",
        "сделать", "заменить", "дополнить", "сократить", "расширить",
        "поэтично", "красиво", "выразительно", "лучше", "стиль",
        "грамматика", "орфография", "пунктуация", "синтаксис"
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in editing_keywords)

def create_json_system_prompt(has_context: bool = False, context_chapter: str = "") -> str:
    """
    Создает системный промпт для работы с JSON-форматом ответов.
    """
    base_prompt = """Вы — AI-редактор текста. 

ФОРМАТ ВХОДА (role=user):
```json
{ 
  "fragment": "<текст для редактирования>", 
  "request": "<что изменить?>" 
}
```

ФОРМАТ ВЫХОДА (role=assistant) - ТОЛЬКО валидный JSON:
```json
{
  "suggestions": [
    { "id": 1, "original": "<оригинальный текст>", "text": "<улучшенный вариант 1>" },
    { "id": 2, "original": "<оригинальный текст>", "text": "<улучшенный вариант 2>" }
  ]
}
```

ПРАВИЛА:
1. Всегда ровно 2-3 элемента в массиве suggestions
2. Никакого markdown, никакого лишнего текста вокруг JSON
3. Если запрос некорректен: {"error": "Выделите фрагмент и опишите задачу"}
4. Работайте ТОЛЬКО с редактурой текста - никакого оффтопа
5. Запрещена обсценная лексика
6. Сохраняйте исходный смысл, делайте текст более выразительным
7. В поле "original" указывайте точный фрагмент для замены"""

    if has_context and context_chapter:
        context_addition = f"\n\nКОНТЕКСТ КНИГИ для понимания стиля:\n---\n{context_chapter}\n---"
        return base_prompt + context_addition
    
    return base_prompt

# Добавляем обработчик OPTIONS для CORS
@router.options("/edit-chat")
async def options_edit_chat():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

# Инициализация клиента для Azure OpenAI
# Убедитесь, что переменные окружения установлены:
# AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Предполагается, что имена деплоев совпадают с именами моделей
# или заданы в переменных окружения
EDIT_MODEL_DEPLOYMENT = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt-4.1-mini")
CHAT_MODEL_DEPLOYMENT = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt-4.1-mini")

class EditRequest(BaseModel):
    text: str
    instruction: str

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

class ModerateRequest(BaseModel):
    input: str

@router.post("/edit-text")
async def edit_text(req: EditRequest):
    """
    Применяет инструкцию к тексту, используя модель чата.
    (API для /edits считается устаревшим).
    """
    completion = await client.chat.completions.create(
        model=EDIT_MODEL_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a text editor. You will receive a text and an instruction. You must apply the instruction to the text. Return only the full, edited text. Do not add any commentary, preamble, or explanation."},
            {"role": "user", "content": f"INSTRUCTION: {req.instruction}\n\nTEXT TO EDIT:\n---\n{req.text}"}
        ]
    )
    return {"text": completion.choices[0].message.content}


@router.post("/edit-chat")
async def chat_edit(req: ChatRequest):
    """
    Ведет диалог с пользователем в режиме стриминга (SSE).
    """
    # Проверяем последнее сообщение пользователя на соответствие политике контента
    if req.messages:
        last_user_message = None
        for msg in reversed(req.messages):
            if msg.get("role") == "user":
                last_user_message = msg
                break
        
        if last_user_message:
            is_allowed, reason = check_content_policy(last_user_message.get("content", ""))
            if not is_allowed:
                async def policy_violation_response():
                    yield f"❌ {reason}\n\nИзвините, я помогаю только с литературной редактурой текста. Пожалуйста, предоставьте фрагмент текста для улучшения."
                
                return StreamingResponse(policy_violation_response(), media_type="text/event-stream")
    
    # Логируем размер запроса для диагностики
    total_chars = sum(len(msg.get("content", "")) for msg in req.messages)
    print(f"🔍 Отправляем {len(req.messages)} сообщений, общий размер: {total_chars} символов")
    
    # Если сообщений слишком много, оставляем только последние
    messages_to_send = req.messages
    if len(req.messages) > 10:
        # Оставляем системное сообщение (первое) + последние 8 сообщений
        system_msg = req.messages[0] if req.messages and req.messages[0].get("role") == "system" else None
        recent_messages = req.messages[-8:]
        messages_to_send = [system_msg] + recent_messages if system_msg else recent_messages
        print(f"📉 Сократили до {len(messages_to_send)} сообщений")
    
    async def event_generator():
        try:
            stream = await client.chat.completions.create(
                model=CHAT_MODEL_DEPLOYMENT,
                messages=messages_to_send,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"An error occurred during streaming: {e}")
            yield f"❌ Произошла ошибка при обработке запроса. Попробуйте еще раз."

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/moderate")
async def moderate_text(req: ModerateRequest):
    """
    Проверяет текст на соответствие политике OpenAI.
    """
    try:
        response = await client.moderations.create(input=req.input)
        result = response.results[0]
        return {"flagged": result.flagged}
    except Exception as e:
        print(f"Ошибка модерации: {e}")
        # Если сервис модерации падает, лучше не блокировать пользователя.
        return {"flagged": False, "error": str(e)}

# Добавляем обработчик OPTIONS для CORS
@router.options("/moderate")
async def options_moderate():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    ) 