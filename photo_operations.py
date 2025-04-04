from datetime import datetime
from typing import Optional

from PIL import Image
from PIL.ExifTags import TAGS
from pydantic import BaseModel, Field


class EXIF(BaseModel):
    camera_model: str | None = Field(None, alias="Model")
    shutter_speed_float: float | None = Field(None, alias="ShutterSpeedValue")
    aperture_float: float | None = Field(None, alias="ApertureValue")
    date_str: str | None = Field(None, alias="DateTimeOriginal")
    focal_length_raw: float | tuple[int, int] | None = Field(None, alias="FocalLength")
    lens_model: str | None = Field(None, alias="LensModel")
    iso: int | None = Field(None, alias="ISOSpeedRatings")
    tags16: bytes | None = Field(None, alias="XPKeywords")

    @property
    def tags(self):
        if self.tags16 is None:
            return None
        try:
            tags = self.tags16.decode("utf-16").strip("\x00")
            return tags.replace(";", " ")
        except Exception:
            return None

    @property
    def focal_length(self):
        if self.focal_length_raw is None:
            return None
        if isinstance(self.focal_length_raw, tuple):
            return f"{int(self.focal_length_raw[0])} mm"
        elif isinstance(self.focal_length_raw, (float, int)):
            return f"{int(self.focal_length_raw)} mm"
        return None

    @property
    def shutter_speed(self) -> Optional[str]:
        if self.shutter_speed_float is None:
            return None
        speed = 2 ** (-self.shutter_speed_float)
        return f"{speed:.0f} сек" if speed >= 1 else f"1/{int(round(1 / speed))}"

    @property
    def aperture(self) -> Optional[str]:
        if self.aperture_float is None:
            return None
        return f"f/{2 ** (self.aperture_float / 2):.1f}"

    @property
    def date(self) -> Optional[str]:
        if self.date_str is None:
            return None
        dt = datetime.strptime(self.date_str, "%Y:%m:%d %H:%M:%S")
        return dt.strftime("%d.%m.%Y")


def get_exif_data(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()

        if exif_data:
            exif = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                exif[tag_name] = value
            return exif
        else:
            return None
    except Exception:
        return None


def get_photocaption(image_path):
    exif = get_exif_data(image_path)
    if exif:
        exif_model = EXIF.model_validate(exif)
        data = {
            "Дата": exif_model.date,
            "Камера": exif_model.camera_model,
            "Объектив": exif_model.lens_model,
            "Выдержка": exif_model.shutter_speed,
            "Диафрагма": exif_model.aperture,
            "Фокусное расстояние": exif_model.focal_length,
            "ISO": exif_model.iso,
            "Теги": exif_model.tags,
        }
        caption = "\n".join([f"{k}: {v}" for k, v in data.items() if v is not None])
        return caption
    return None
