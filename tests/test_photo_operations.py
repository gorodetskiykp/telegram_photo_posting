import pytest
from PIL import Image
from io import BytesIO
import piexif
from photo_operations import EXIF, get_exif_data, get_photocaption


@pytest.fixture
def sample_image_with_exif():
    img = Image.new("RGB", (100, 100), color="red")

    # Создаем EXIF данные
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Model: "Test Camera",
            piexif.ImageIFD.DateTime: "2023:01:15 12:00:00",
            40094: "test;keywords".encode("utf-16le") + b"\x00\x00",
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: "2023:01:15 12:00:00",
            piexif.ExifIFD.FocalLength: (50, 1),
            piexif.ExifIFD.ISOSpeedRatings: 100,
            piexif.ExifIFD.ShutterSpeedValue: (6643856, 1000000),
            piexif.ExifIFD.ApertureValue: (4, 1),
            piexif.ExifIFD.LensModel: "Test Lens",
        },
    }

    # Сохраняем с EXIF
    exif_bytes = piexif.dump(exif_dict)
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG", exif=exif_bytes)
    img_bytes.seek(0)

    return img_bytes


def test_exif_model_parsing(sample_image_with_exif):
    """Тестирование корректного парсинга EXIF данных"""
    exif_data = get_exif_data(sample_image_with_exif)
    exif_model = EXIF.model_validate(exif_data)

    assert exif_model.camera_model == "Test Camera"
    assert exif_model.lens_model == "Test Lens"
    assert exif_model.iso == 100


def test_properties_calculation(sample_image_with_exif):
    """Тестирование вычисляемых свойств"""
    exif_data = get_exif_data(sample_image_with_exif)
    exif_model = EXIF.model_validate(exif_data)

    assert exif_model.focal_length == "50 mm"
    assert exif_model.shutter_speed == "1/100"
    assert exif_model.aperture == "f/4.0"
    assert exif_model.date == "15.01.2023"
    assert exif_model.tags == "test keywords"


def test_get_photocaption(sample_image_with_exif):
    """Тестирование формирования подписи"""
    caption = get_photocaption(sample_image_with_exif)

    assert "Камера: Test Camera" in caption
    assert "Объектив: Test Lens" in caption
    assert "ISO: 100" in caption
    assert "Фокусное расстояние: 50 mm" in caption
    assert "Теги: test keywords" in caption


def test_empty_exif_handling():
    """Тестирование обработки отсутствия EXIF"""
    img = Image.new("RGB", (100, 100))
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    assert get_exif_data(img_bytes) is None
    assert get_photocaption(img_bytes) is None


def test_partial_exif_handling():
    """Тестирование обработки частичных EXIF данных"""
    img = Image.new("RGB", (100, 100))
    exif_dict = {"0th": {piexif.ImageIFD.Model: "Partial Camera"}}
    exif_bytes = piexif.dump(exif_dict)

    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG", exif=exif_bytes)
    img_bytes.seek(0)

    caption = get_photocaption(img_bytes)
    assert "Камера: Partial Camera" in caption
    assert "ISO:" not in caption  # Поле отсутствует
