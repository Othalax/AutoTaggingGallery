from PySide6.QtCore import QThread, Signal
import time
import fileManager

class ImportWorker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, filepaths, file_manager, database_manager, detector):
        super().__init__()
        self.filepaths = filepaths
        self.file_manager = file_manager
        self.database_manager = database_manager
        self.detector = detector

    def run(self):
        try:
            for filepath in self.filepaths:
                original_name, unique_name = self.file_manager.import_photo(filepath)
                tags = self.detector.detect_tags(filepath)
                self.database_manager.add_photo(original_name, unique_name, tags)
                time.sleep(0.05)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class DeleteWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, filepath, database_manager):
        super().__init__()
        self.filepath = filepath
        self.database_manager = database_manager

    def run(self):
        try:
            fileManager.delete_photo(self.filepath)
            self.database_manager.delete_photo_by_filepath(self.filepath)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit(self.filepath)