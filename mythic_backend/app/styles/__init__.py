from importlib import import_module

ALLOWED_STYLES = {
    'romantic': 'romantic',
    'fantasy': 'fantasy',
    'humor': 'humor',
}

def build_book(style: str, run_id: str, images, comments, book_format: str = 'classic', user_id: str = None):
    """Делегирует создание книги модулю конкретного стиля.
    Если стиль неизвестен – падаем на романтический."""
    module_name = ALLOWED_STYLES.get(style, 'romantic')
    module = import_module(f'app.styles.{module_name}')
    if hasattr(module, 'build_book'):
        return module.build_book(run_id, images, comments, book_format, user_id)
    else:
        raise ImportError(f'Module {module_name} does not implement build_book') 