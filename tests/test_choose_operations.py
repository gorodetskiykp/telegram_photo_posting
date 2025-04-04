import json

import pytest

from choose_operations import choose_photo, mark_posted_photo


@pytest.fixture
def posted_file(tmp_path):
    """
    Фикстура создает временный файл для тестирования.
    """
    file_path = tmp_path / "posted_photos.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({}, f)
    return file_path


def test_mark_posted_photo_new_photo(posted_file, monkeypatch):
    """
    Тестирование добавления нового фото.
    """
    # Мокаем глобальную переменную POSTED
    monkeypatch.setattr("choose_operations.POSTED", str(posted_file))

    photo_path = "photo1.jpg"
    mark_posted_photo(photo_path)

    with open(posted_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data[photo_path] == 1


def test_mark_posted_photo_existing_photo(posted_file, monkeypatch):
    """
    Тестирование увеличения счетчика для существующего фото.
    """
    monkeypatch.setattr("choose_operations.POSTED", str(posted_file))

    photo_path = "photo1.jpg"
    # Добавляем фото первый раз
    mark_posted_photo(photo_path)
    # Добавляем второй раз
    mark_posted_photo(photo_path)

    with open(posted_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data[photo_path] == 2


def test_mark_posted_photo_no_file(tmp_path, monkeypatch):
    """
    Тестирование случая, когда файл не существует.
    """
    file_path = tmp_path / "nonexistent.json"
    monkeypatch.setattr("choose_operations.POSTED", str(file_path))

    photo_path = "photo1.jpg"
    mark_posted_photo(photo_path)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data[photo_path] == 1


def test_choose_photo_no_history(posted_file, monkeypatch):
    """
    Тестирование выбора фото, когда нет истории публикаций.
    """
    monkeypatch.setattr("choose_operations.POSTED", str(posted_file))

    photos = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
    chosen = choose_photo(photos)

    assert chosen in photos


def test_choose_photo_with_history(posted_file, monkeypatch):
    """
    Тестирование выбора фото с учетом истории публикаций.
    """
    monkeypatch.setattr("choose_operations.POSTED", str(posted_file))

    # Создаем историю публикаций
    history = {
        "photo1.jpg": 3,
        "photo2.jpg": 1,
        "photo3.jpg": 0,  # это фото никогда не публиковалось
    }
    with open(posted_file, "w", encoding="utf-8") as f:
        json.dump(history, f)

    photos = list(history.keys())
    results = {photo: 0 for photo in photos}

    # Многократный выбор для проверки распределения
    for _ in range(1000):
        chosen = choose_photo(photos)
        results[chosen] += 1

    # Проверяем, что photo3.jpg выбирается чаще, чем photo1.jpg
    assert results["photo3.jpg"] > results["photo1.jpg"]
    # photo2.jpg должен выбираться реже, чем photo3.jpg,
    # но чаще, чем photo1.jpg
    assert results["photo3.jpg"] > results["photo2.jpg"] > results["photo1.jpg"]


def test_choose_photo_corrupted_file(tmp_path, monkeypatch):
    """
    Тестирование выбора фото при поврежденном файле истории.
    """
    file_path = tmp_path / "corrupted.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{invalid json")

    monkeypatch.setattr("choose_operations.POSTED", str(file_path))

    photos = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
    chosen = choose_photo(photos)

    assert chosen in photos
    # Проверяем, что файл был перезаписан
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {}
