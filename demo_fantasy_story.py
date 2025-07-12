#!/usr/bin/env python3
"""
Демонстрация фантастической истории в новом читабельном стиле
"""

from pathlib import Path
import json
from mythic_backend.app.styles.fantasy import generate_fantasy_chapters, create_fantasy_html

def create_demo_fantasy_story():
    """Создает демонстрационную фантастическую историю"""
    
    # Демо-данные профиля
    demo_analysis = {
        "full_name": "Александр Светлый",
        "username": "alex_hero",
        "bio": "Искатель приключений и хранитель древних знаний",
        "followers": 1234,
        "posts": [],
        "profile_pic": ""
    }
    
    print("🔮 Создание демонстрационной фантастической истории...")
    
    # Генерируем главы
    chapters = generate_fantasy_chapters(demo_analysis, [])
    
    print("\n📖 Сгенерированные главы:")
    for key, content in chapters.items():
        print(f"\n--- {key.upper()} ---")
        print(content[:200] + "..." if len(content) > 200 else content)
    
    # Создаем HTML
    html = create_fantasy_html(demo_analysis, chapters, [])
    
    # Сохраняем демо-файл
    demo_file = Path("demo_fantasy_story.html")
    demo_file.write_text(html, encoding="utf-8")
    
    print(f"\n✅ Демо-история сохранена в {demo_file}")
    print("Откройте файл в браузере, чтобы увидеть красивую фантастическую книгу!")
    
    return chapters

if __name__ == "__main__":
    create_demo_fantasy_story() 