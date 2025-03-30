# telegram_photo_posting

1. python -m venv venv
2. venv\Scripts\activate
3. pip install -r requirements.txt
4. Создать каталоги
    - photos - поместить в каталог фото
    - posted_photos
    - resized_photos
5. Завести два теле-бота
    - для публикации локальных фото в канале
    - для репоста фото из канала в группу ВК
6. Завести телеграм-канал
7. Добавить оба бота в админи канала
8. Создать файл creds.py, добавить токен первого бота в TELEGRAM_TOKEN
9. Настроить Планировщик задач Windows для запуска скрипта по расписанию
10. Настроить https://onemorepost.ru для репоста в ВК