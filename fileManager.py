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

    def get_photos(self, batch_size=8):
        if not os.path.exists(self.storage_dir):
            return

        valid_extensions = ('.jpg', '.png')
        current_batch = []

        for file_name in os.listdir(self.storage_dir):
            if os.path.splitext(file_name)[1].lower() in valid_extensions:
                full_path = os.path.join(self.storage_dir, file_name)
                current_batch.append(full_path)

                if len(current_batch) == batch_size:
                    yield current_batch
                    current_batch = []

        if current_batch:
            yield current_batch