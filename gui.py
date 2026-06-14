import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QHBoxLayout,
                               QVBoxLayout, QWidget, QLineEdit, QGridLayout, QFileDialog,
                               QScrollArea, QLabel, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import database
import fileManager
import detection


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

        self.current_photos = []
        self.photo_generator = None
        self.update_photos_list()

    def showEvent(self, event):
        super().showEvent(event)

        available_width = self.scroll_area.viewport().width()
        self.max_columns = max(1, available_width // 100)

        self.update_photos_list(self.search_bar.text())

    def resizeEvent(self, event):
        super().resizeEvent(event)

        available_width = self.scroll_area.viewport().width()
        new_max_columns = max(1, available_width // 100)

        if new_max_columns != self.max_columns:
            self.max_columns = new_max_columns
            self.reorganize_grid()

        super().resizeEvent(event)

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
        action_delete = menu.addAction("Delete")

        action = menu.exec(self.cursor().pos())

        if action == action_view:
            print(f"Details for {filepath}")
        elif action == action_delete:
            self.delete_image(filepath)

    def delete_image(self, filepath):
        fileManager.delete_photo(filepath, database_manager, self.current_photos)
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
        filepath, _ = QFileDialog.getOpenFileName(self, "Select the picture", "", "Images (*.png *.jpg)")

        if filepath:
            original_name, unique_name = file_manager.import_photo(filepath)
            tags = detector.detect_tags(filepath)
            database_manager.add_photo(original_name, unique_name, tags)

            self.update_photos_list(self.search_bar.text())

    def update_photos_list(self, filter_text=""):
        self.clear_gallery()

        if filter_text.strip():
            self.current_photos = database_manager.get_photos_by_tag(filter_text)
        else:
            self.current_photos = database_manager.get_all_photos()

        self.photo_generator = file_manager.get_photos(
            self.current_photos, batch_size=16, database_manager=database_manager
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