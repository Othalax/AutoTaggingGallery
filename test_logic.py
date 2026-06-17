import os
import pytest
from unittest.mock import MagicMock, patch
import database
import fileManager
import detection
from workers import ImportWorker

@pytest.fixture(scope="function")
def isolated_env(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    app_dir = tmp_path / "AutoTaggingGallery"
    app_dir.mkdir()
    return tmp_path

@pytest.fixture(scope="function")
def db_manager(isolated_env):
    return database.DatabaseManager("test_gallery.db")


def test_add_and_get_photo(db_manager):
    photo_id = db_manager.add_photo("wakacje.jpg", "uuid123.jpg", ["Pies", "kot", " Drzewo "])
    assert photo_id is not None

    photos = db_manager.get_all_photos()
    assert len(photos) == 1
    assert photos[0]["original_name"] == "wakacje.jpg"
    assert photos[0]["stored_name"] == "uuid123.jpg"

def test_tags_are_cleaned_and_saved(db_manager):
    db_manager.add_photo("test.jpg", "test.jpg", ["  Dog  ", "CAT", ""])
    tags = db_manager.get_tags_for_photo("test.jpg")

    assert len(tags) == 2
    assert "dog" in tags
    assert "cat" in tags

def test_cascade_delete_photo(db_manager):
    photo_id = db_manager.add_photo("test.jpg", "test.jpg", ["dog"])
    db_manager.delete_photo(photo_id)

    assert len(db_manager.get_all_photos()) == 0
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM photo_tags")
        assert len(cursor.fetchall()) == 0


@pytest.mark.parametrize("file_name, expected_ext", [
    ("test.jpg", ".jpg"),
    ("photo.png", ".png"),
    ("UPPERCASE.JPG", ".jpg")])

def test_validate_file_success(tmp_path, file_name, expected_ext):
    p = tmp_path / file_name
    p.write_text("fake_image_data")

    ext = fileManager.validate_file(str(p))
    assert ext == expected_ext


def test_validate_file_not_found():
    with pytest.raises(FileNotFoundError):
        fileManager.validate_file("nie_ma_takiego_pliku.jpg")


def test_validate_file_wrong_extension(tmp_path):
    p = tmp_path / "dokument.txt"
    p.write_text("Hello")

    with pytest.raises(ValueError):
        fileManager.validate_file(str(p))


def test_import_photo(isolated_env, tmp_path):
    fm = fileManager.FileManager()

    p = tmp_path / "test_photo.jpg"
    p.write_text("fake_image_data")

    original_name, unique_name = fm.import_photo(str(p))

    assert original_name == "test_photo.jpg"
    assert unique_name.endswith(".jpg")

    expected_path = os.path.join(fm.storage_dir, unique_name)
    assert os.path.exists(expected_path)


@patch("detection.YOLO")
def test_detect_tags_filtering(mock_yolo_class, isolated_env):
    mock_model_instance = MagicMock()
    mock_yolo_class.return_value = mock_model_instance

    mock_box1 = MagicMock()
    mock_box1.conf = [0.8]
    mock_box1.cls = [0]

    mock_box2 = MagicMock()
    mock_box2.conf = [0.1]
    mock_box2.cls = [1]

    mock_result = MagicMock()
    mock_result.boxes = [mock_box1, mock_box2]
    mock_result.names = {0: "polar_bear", 1: "penguin"}

    mock_model_instance.return_value = [mock_result]

    detector = detection.Detector()
    tags = detector.detect_tags("fake_path.jpg")

    assert len(tags) == 1
    assert "polar bear" in tags
    assert "penguin" not in tags


def test_import_worker(qtbot):
    mock_file_manager = MagicMock()
    mock_file_manager.import_photo.return_value = ("test.jpg", "unique.jpg")
    mock_detector = MagicMock()
    mock_database = MagicMock()

    worker = ImportWorker(["fake_path.jpg"], mock_file_manager, mock_database, mock_detector)

    with qtbot.waitSignal(worker.finished, timeout=2000):
        worker.start()

    mock_database.add_photo.assert_called_once()
