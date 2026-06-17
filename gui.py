import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QHBoxLayout,
                               QVBoxLayout, QWidget, QLineEdit, QGridLayout, QFileDialog,
                               QScrollArea, QLabel, QMenu, QDialog, QMessageBox)
from PySide6.QtCore import Qt, QUrl, QMimeData
from PySide6.QtGui import QPixmap
import database
import fileManager
import detection


class PhotoDetails(QDialog):
    def __init__(self, filepath):
        super().__init__()
        self.setWindowTitle("Photo details")
        self.resize(300, 200)
        self.filepath = filepath

        layout = QVBoxLayout()

        label = QLabel()
        pixmap = QPixmap(filepath)
        scaled_pixmap = pixmap.scaled(
            500,
            500,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        tags_list = database_manager.get_tags_for_photo(filepath)
        tags_str = ""
        for tag in tags_list:
            if tags_str:
                tags_str += ", "
            tags_str += tag
        tags = QLabel("Tags: " + tags_str)
        download_button = QPushButton("Download photo")

        layout.addWidget(label)
        layout.addWidget(tags)
        layout.addWidget(download_button)

        self.setLayout(layout)

        download_button.clicked.connect(self.download_photo)

    def download_photo(self):
        original_name = database_manager.get_original_name(self.filepath)


        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            "Download Photo",
            original_name
        )

        if dest_path:
            try:
                fileManager.export_photo(self.filepath, dest_path)
                QMessageBox.information(self, "Success", "Photo downloaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not download photo: {e}")

class AutoTaggingGallery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Tagging Gallery")
        self.resize(1000, 600)

        main_layout = QVBoxLayout()

        menu_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by tag")
        menu_layout.addWidget(self.search_bar)
        self.add_button = QPushButton("Add picture")
        menu_layout.addWidget(self.add_button)

        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.gallery_widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.scroll_area, stretch=2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.search_bar.textChanged.connect(self.search_images)
        self.add_button.clicked.connect(self.add_file)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

        self.current_row = 0
        self.current_col = 0
        self.max_columns = 10
        self.max_rows = 6

        self.current_photos = []
        self.photo_generator = None
        self.update_photos_list()

        self.photo_details = None

    def showEvent(self, event):
        super().showEvent(event)

        available_width = self.scroll_area.viewport().width()
        self.max_columns = max(1, available_width // 105)
        available_height = self.scroll_area.viewport().height()
        self.max_rows = max(1, available_height // 105) + 1

        self.update_photos_list(self.search_bar.text())

    def resizeEvent(self, event):
        super().resizeEvent(event)

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()
        try:
            available_width = self.scroll_area.viewport().width()
            new_max_columns = max(1, available_width // 105)
            available_height = self.scroll_area.viewport().height()
            self.max_rows = max(1, available_height // 105) + 1

            if new_max_columns < self.max_columns:
                self.max_columns = new_max_columns
                self.reorganize_grid()

            if new_max_columns > self.max_columns:
                self.max_columns = new_max_columns
                self.update_photos_list(self.search_bar.text())
        finally:
            QApplication.restoreOverrideCursor()

    def reorganize_grid(self):
        widgets = []
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widgets.append(widget)

        self.current_row = 0
        self.current_col = 0

        for widget in widgets:
            self.gallery_layout.addWidget(widget, self.current_row, self.current_col)
            self.current_col += 1
            if self.current_col >= self.max_columns:
                self.current_col = 0
                self.current_row += 1

    def on_scroll(self, value):
        if value == self.scroll_area.verticalScrollBar().maximum():
            self.load_next_batch()

    def add_photo_to_grid(self, filepath):
        label = QLabel()
        label.setProperty("filepath", filepath)
        label.installEventFilter(self)
        pixmap = QPixmap(filepath)

        size = min(pixmap.width(), pixmap.height())

        x = (pixmap.width() - size) // 2
        y = (pixmap.height() - size) // 2

        cropped_pixmap = pixmap.copy(x, y, size, size)
        scaled_pixmap = cropped_pixmap.scaled(
            100, 100,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        label.setPixmap(scaled_pixmap)
        label.setStyleSheet("border: 1px solid #ccc; padding: 1px; background: #f0f0f0;")
        label.setFixedSize(100, 100)

        self.gallery_layout.addWidget(label, self.current_row, self.current_col)

        self.current_col += 1
        if self.current_col >= self.max_columns:
            self.current_col = 0
            self.current_row += 1

    def eventFilter(self, watched, event):
        if event.type() == event.Type.MouseButtonPress:
            mouse_event = event
            if mouse_event.button() == Qt.MouseButton.RightButton:
                filepath = watched.property("filepath")
                if filepath:
                    self.show_image_options(filepath)
                    return True

        return super().eventFilter(watched, event)

    def show_image_options(self, filepath):
        menu = QMenu(self)
        action_view = menu.addAction("Show details")
        action_copy = menu.addAction("Copy to clipboard")
        menu.addSeparator()
        action_delete = menu.addAction("Delete")

        action = menu.exec(self.cursor().pos())

        if action == action_view:
            self.show_image_details(filepath)

        elif action == action_copy:
            mime_data = QMimeData()
            url = QUrl.fromLocalFile(filepath)
            mime_data.setUrls([url])

            clipboard = QApplication.clipboard()
            clipboard.setMimeData(mime_data)

        elif action == action_delete:
            self.delete_image(filepath)

    def show_image_details(self, filepath):
        self.photo_details = PhotoDetails(filepath)
        self.photo_details.exec()

    def delete_image(self, filepath: str):
        fileManager.delete_photo(filepath)
        database_manager.delete_photo_by_filepath(filepath)
        self.update_photos_list()

    def clear_gallery(self):
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.current_row = 0
        self.current_col = 0

    def add_file(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Select the picture", "", "Images (*.png *.jpg)")

        if filepaths:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            QApplication.processEvents()

            try:
                for filepath in filepaths:
                    original_name, unique_name = file_manager.import_photo(filepath)
                    tags = detector.detect_tags(filepath)
                    database_manager.add_photo(original_name, unique_name, tags)

                self.update_photos_list(self.search_bar.text())
            finally:
                QApplication.restoreOverrideCursor()

    def update_photos_list(self, filter_text=""):
        self.clear_gallery()

        if filter_text.strip():
            self.current_photos = database_manager.get_photos_by_tag(filter_text)
        else:
            self.current_photos = database_manager.get_all_photos()

        batch_size = self.max_columns * self.max_rows
        self.photo_generator = file_manager.get_photos(
            self.current_photos, batch_size=batch_size, database_manager=database_manager
        )

        self.load_next_batch()

    def load_next_batch(self):
        if not self.photo_generator:
            return

        try:
            batch = next(self.photo_generator)
            for filepath in batch:
                self.add_photo_to_grid(filepath)
        except StopIteration:
            pass

    def search_images(self, text):
        self.update_photos_list(text)


if __name__ == "__main__":
    file_manager = fileManager.FileManager()
    database_manager = database.DatabaseManager()
    detector = detection.Detector()
    app = QApplication(sys.argv)
    window = AutoTaggingGallery()
    window.show()
    sys.exit(app.exec())