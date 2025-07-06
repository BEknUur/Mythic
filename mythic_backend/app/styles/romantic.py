from app.services.book_builder import build_romantic_book


def build_book(run_id: str, images, comments, book_format: str = 'classic', user_id: str = None):
    """Прокси к существующему романтическому генератору"""
    return build_romantic_book(run_id, images, comments, book_format, user_id) 