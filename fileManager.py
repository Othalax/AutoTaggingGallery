import os
import shutil
import uuid


class FileManager:
    def __init__(self, app_name="AutoTaggingGallery"):
        appdata_dir = os.getenv('APPDATA')

        self.storage_dir = os.path.join(appdata_dir, app_name, "photos")
        os.makedirs(self.storage_dir, exist_ok=True)

    def validate_file(self, source_path):
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Wybrany plik nie istnieje: {source_path}")

        valid_extensions = ('.jpg', '.png')
        ext = os.path.splitext(source_path)[1].lower()

        if ext not in valid_extensions:
            raise ValueError(f"Niepoprawny format pliku. Akceptowane: {', '.join(valid_extensions)}")

        return ext

    def import_photo(self, source_path):
        ext = self.validate_file(source_path)

        original_name = os.path.basename(source_path)

        unique_name = f"{uuid.uuid4().hex}{ext}"

        destination_path = os.path.join(self.storage_dir, unique_name)
        shutil.copy(source_path, destination_path)

        return original_name, unique_name

    def get_full_path(self, stored_name):
        return os.path.join(self.storage_dir, stored_name)

    def get_photos_by_lazy_generator(self, photos_metadata, batch_size, database_manager):
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