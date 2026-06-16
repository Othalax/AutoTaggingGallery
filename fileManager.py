import os
import shutil
import uuid


def validate_file(source_path):
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Selected file does not exist: {source_path}")

    valid_extensions = ('.jpg', '.png')
    ext = os.path.splitext(source_path)[1].lower()

    if ext not in valid_extensions:
        raise ValueError(f"Invalid file format. Accepted: {', '.join(valid_extensions)}")

    return ext


def delete_photo(filepath, database_manager, photos_metadata):
    stored_name = os.path.basename(filepath)

    photo_id = None
    for photo in photos_metadata:
        if photo['stored_name'] == stored_name:
            photo_id = photo['id']
            break

    if photo_id is not None:
        database_manager.delete_photo(photo_id)
    else:
        raise KeyError(f"No photo named {stored_name} in database.")

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError as e:
            print(f"Error deleting file from disk: {e}")


def export_photo(source_path, destination_path):
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file does not exist: {source_path}")

    shutil.copy(source_path, destination_path)


class FileManager:
    def __init__(self):
        appdata_dir = os.getenv('APPDATA')

        self.storage_dir = os.path.join(appdata_dir, "AutoTaggingGallery", "photos")
        os.makedirs(self.storage_dir, exist_ok=True)

    def import_photo(self, source_path):
        ext = validate_file(source_path)

        original_name = os.path.basename(source_path)

        unique_name = f"{uuid.uuid4().hex}{ext}"

        destination_path = os.path.join(self.storage_dir, unique_name)
        shutil.copy(source_path, destination_path)

        return original_name, unique_name

    def get_full_path(self, stored_name):
        return os.path.join(self.storage_dir, stored_name)

    def get_photos(self, photos_metadata, batch_size, database_manager):
        current_batch = []

        for photo in photos_metadata:
            full_path = self.get_full_path(photo['stored_name'])

            if not os.path.exists(full_path):
                database_manager.delete_photo(photo['id'])
                continue

            current_batch.append(full_path)
            if len(current_batch) == batch_size:
                yield current_batch
                current_batch = []

        if current_batch:
            yield current_batch

