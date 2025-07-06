import json
from pathlib import Path


def collect_texts(json_path: Path) -> str:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    texts = []
    for item in data:
        # Собираем тексты из постов
        for post in item.get("latestPosts", []):
            if cap := post.get("caption"):
                texts.append(cap)
            for cm in post.get("latestComments", []):
                if txt := cm.get("text"):
                    texts.append(txt)
        
        # Собираем тексты из сторисов
        for story in item.get("stories", []):
            if story_text := story.get("text"):
                texts.append(f"[История] {story_text}")
            # Если есть подпись к сторису
            if story_caption := story.get("caption"):
                texts.append(f"[История] {story_caption}")
    
    return "\n\n".join(texts)
