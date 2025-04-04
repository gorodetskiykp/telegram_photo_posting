import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PIL import Image
from telegram import Bot
from telegram.error import TelegramError
from telegram.request import HTTPXRequest

from choose_operations import choose_photo, mark_posted_photo
from creds import TELEGRAM_TOKEN
from files_operations import find_all_files
from photo_operations import get_photocaption
from settings import (
    CHAT_ID,
    IMAGE_EXT,
    PHOTO_FOLDER,
    POST_TAGS,
    RESIZED_PHOTO_FOLDER,
)

# Создание логгера
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)  # Минимальный уровень логирования

# Создание форматтера
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Создание консольного обработчика
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # В консоль только INFO и выше
console_handler.setFormatter(formatter)

# Создание файлового обработчика с ротацией
file_handler = RotatingFileHandler("main.log", maxBytes=1024 * 1024, backupCount=5)  # 1MB per file, 5 backups
file_handler.setLevel(logging.DEBUG)  # В файл пишем всё
file_handler.setFormatter(formatter)

# Добавление обработчиков к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)


async def auto_post_photos():
    is_resized = False

    # Инициализация бота
    bot = Bot(
        token=TELEGRAM_TOKEN,
        request=HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, write_timeout=30.0),
    )

    photos = find_all_files(IMAGE_EXT, PHOTO_FOLDER)
    photo_path = choose_photo(photos)
    logger.info(photo_path)
    with Image.open(photo_path) as img:
        logger.info(f"{img.size=}")
        if max(img.size) > 4096:
            logger.info("Resize")
            exif = img.getexif()
            img.thumbnail((2048, 2048))
            resized_photo_path = Path(RESIZED_PHOTO_FOLDER) / photo_path.name
            img.save(resized_photo_path, "JPEG", quality=100, exif=exif)
            photo_path = resized_photo_path
            is_resized = True
    try:
        with open(photo_path, "rb") as file:
            caption = get_photocaption(Path(photo_path))
            logger.info(caption)
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=file,
                filename=os.path.basename(photo_path),
                caption=f"{caption}\n\n{POST_TAGS}",
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
            )
        logger.info("Posted")
    except TelegramError as e:
        logger.error(f"Error: {e}")
        raise
    if is_resized:
        photo_path = Path(PHOTO_FOLDER) / photo_path.name
        os.remove(resized_photo_path)
    mark_posted_photo(photo_path)


if __name__ == "__main__":
    asyncio.run(auto_post_photos())
