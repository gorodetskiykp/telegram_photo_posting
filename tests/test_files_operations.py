from pathlib import Path
import tempfile
import pytest

from files_operations import find_all_files


@pytest.fixture
def temp_dir():
    # Создаем временную директорию с тестовыми файлами
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Создаем файлы разных расширений
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.TXT").touch()
        (tmp_path / "image1.jpg").touch()
        (tmp_path / "image2.JPG").touch()
        (tmp_path / "document.pdf").touch()

        # Создаем поддиректорию с файлами
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").touch()
        (subdir / "image3.png").touch()

        yield tmp_path  # Возвращаем путь к временной директории


@pytest.mark.parametrize(
    "ext,expected_count",
    [
        (["txt"], 3),
        (["jpg"], 2),
        (["pdf"], 1),
        (["png"], 1),
        (["mp3"], 0),
    ],
)
def test_find_files_parametrized(temp_dir, ext, expected_count):
    result = find_all_files(ext, temp_dir)
    assert len(result) == expected_count


def test_return_type(temp_dir):
    result = find_all_files(["txt"], temp_dir)
    assert all(isinstance(item, Path) for item in result)


def test_nonexistent_directory():
    """Тест обработки несуществующей директории"""
    assert find_all_files(["txt"], "/nonexistent/path") == []
