import json
import random
from pathlib import Path
from typing import Union

from settings import POSTED


def mark_posted_photo(photo_path: Union[str, Path]) -> None:
    """
    Увеличивает счетчик публикаций для указанного фото
    или добавляет новую запись.
    Если файл с данными не существует, создает новый.

    Args:
        photo_path (str): Путь к фото, которое было опубликовано.

    Returns:
        None
    """
    if not isinstance(photo_path, str):
        photo_path = str(photo_path)
    try:
        # Чтение существующих данных
        with open(POSTED, "r", encoding="utf-8") as posted_file:
            posted = json.load(posted_file)

        # Обновление счетчика для фото
        if photo_path in posted:
            posted[photo_path] += 1
        else:
            posted[photo_path] = 1

        # Сохранение обновленных данных
        with open(POSTED, "w", encoding="utf-8") as posted_file:
            json.dump(posted, posted_file, ensure_ascii=False, indent=4)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        json.decoder.JSONDecodeError,
    ):
        # Если файла нет или он поврежден, создаем новый
        with open(POSTED, "w", encoding="utf-8") as posted_file:
            json.dump({}, posted_file)
        # Рекурсивный вызов для повторной попытки
        mark_posted_photo(photo_path)


def choose_photo(photos: list[str]) -> str:
    """
    Выбирает случайное фото из списка, учитывая частоту предыдущих публикаций.
    Фото, которые публиковались реже, имеют больше шансов быть выбранными.

    Args:
        photos (List[str]): Список путей к доступным фото.

    Returns:
        str: Путь к выбранному фото.
    """
    try:
        with open(POSTED, "r", encoding="utf-8") as posted_file:
            posted = json.load(posted_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файла нет или он поврежден, создаем новый
        with open(POSTED, "w", encoding="utf-8") as posted_file:
            json.dump({}, posted_file)
        posted = {}

    if not posted:
        # Если нет данных о публикациях, выбираем случайное фото
        return random.choice(photos)

    max_multiply = max(posted.values()) + 1
    photos_list = []

    # Создаем взвешенный список, где реже публикованные фото встречаются чаще
    for photo in photos:
        photos_list.extend([photo] * (max_multiply - posted.get(photo, 0)))

    # Перемешиваем и выбираем случайное фото
    random.shuffle(photos_list)
    return random.choice(photos_list)
