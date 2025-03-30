from pathlib import Path


def find_all_files(extentions: list[str], folder: str) -> list[Path]:
    extentions = [f".{extention}" for extention in extentions]
    return [
        p.absolute()
        for p in Path(folder).rglob("*") 
        if p.is_file() and p.suffix.lower() in extentions
    ]
