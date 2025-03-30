import asyncio
import logging
import random
import os
import shutil

from logging.handlers import RotatingFileHandler

from PIL import Image
from telegram import Bot
from telegram.error import TelegramError
from telegram.request import HTTPXRequest

from creds import TELEGRAM_TOKEN

# Создание логгера
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)  # Минимальный уровень логирования

# Создание форматтера
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Создание консольного обработчика
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # В консоль только INFO и выше
console_handler.setFormatter(formatter)

# Создание файлового обработчика с ротацией
file_handler = RotatingFileHandler(
    'main.log', maxBytes=1024*1024, backupCount=5  # 1 MB per file, 5 backups
)
file_handler.setLevel(logging.DEBUG)  # В файл пишем всё
file_handler.setFormatter(formatter)

# Добавление обработчиков к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Конфигурация
CHAT_ID = "@ohmyphotos"  # Или ID чата (например, -100123456789)
PHOTO_FOLDER = "photos"
RESIZED_PHOTO_FOLDER = "resized_photos"
POSTED_PHOTO_FOLDER = "posted_photos"


async def auto_post_photos():
    is_resized = False

    # Инициализация бота
    bot = Bot(
        token=TELEGRAM_TOKEN,
        request=HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, write_timeout=30.0)
    )

    # Получаем список файлов в папке
    photos = [
        filename
        for filename in os.listdir(PHOTO_FOLDER)
        if filename.endswith(('.jpg', '.png'))
    ]  # noqa: WPS221
    if photos:
        photo = random.choice(photos)  # noqa: S311
        logger.info(photo)
    else:
        for filename in os.listdir(POSTED_PHOTO_FOLDER):
            src_path = os.path.join(POSTED_PHOTO_FOLDER, filename)
            dst_path = os.path.join(PHOTO_FOLDER, filename)
            # Проверяем, что это файл (а не директория)
            if os.path.isfile(src_path):
                shutil.move(src_path, dst_path)
                logger.info(f"Moved: {src_path} -> {dst_path}")
        photos = [
            filename
            for filename in os.listdir(PHOTO_FOLDER)
            if filename.endswith(('.jpg', '.png'))
        ]  # noqa: WPS221
        photo = random.choice(photos)  # noqa: S311
        logger.info(photo)
    
    photo_path = os.path.join(PHOTO_FOLDER, photo)

    with Image.open(photo_path) as img:
        logger.info(f'{img.size=}')
        if max(img.size) > 4096:
            logger.info('Resize')
            img.thumbnail((2048, 2048))
            resized_photo_path = os.path.join(RESIZED_PHOTO_FOLDER, photo)
            img.save(resized_photo_path, 'JPEG', quality=100)
            photo_path = resized_photo_path
            is_resized = True
    try:
        # Отправка фото в Telegram
        with open(photo_path, 'rb') as file:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=file,
                filename=os.path.basename(photo_path),
                caption="",
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30
            )
        logger.info("Posted")
    except TelegramError as e:
        logger.error(f"Error: {e}")
        raise
    posted_photo_path = os.path.join(POSTED_PHOTO_FOLDER, photo)
    if is_resized:
        photo_path = os.path.join(PHOTO_FOLDER, photo)
        os.remove(resized_photo_path)
    shutil.move(photo_path, posted_photo_path)
    logger.info(f"Moved posted photo: {photo_path} -> {posted_photo_path}")


if __name__ == "__main__":
    asyncio.run(auto_post_photos())
