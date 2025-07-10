# app/services/text_collector.py
import json
from pathlib import Path

def collect_texts(posts_json_path: Path) -> list[str]:
    """
    Из posts.json собираем все доступные подписи и сторисы в один большой список.
    Каждый элемент — это либо caption, либо текст сториса.
    """
    if not posts_json_path.exists():
        print(f"⚠️ Файл {posts_json_path} не найден, тексты не собраны.")
        return []
        
    items = json.loads(posts_json_path.read_text(encoding="utf-8"))
    texts = []
    
    # Instagram Profile Scraper actor returns a list where the first item is the profile
    profile_data = items[0] if items else {}
    posts = profile_data.get("latestPosts", [])

    for post in posts:
        if caption := post.get("caption"):
            texts.append(caption)
    
    # Stories might be in a separate key or within posts
    if stories := profile_data.get("stories"):
        for story in stories:
            # Assuming stories might have text, though the structure can vary
            # This is a placeholder for actual story text extraction logic
            # based on real data structure from Apify.
            # For now, we assume a simple text key might exist.
            if story_text := story.get("text"): # Placeholder key
                 texts.append(story_text)
    
    return texts
