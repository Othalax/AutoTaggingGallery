import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QHBoxLayout,
                               QVBoxLayout, QWidget, QLineEdit, QGridLayout, QFileDialog)


class AutoTaggingGallery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Tagging Gallery")
        self.resize(950, 600)

        main_layout = QVBoxLayout()

        menu_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        menu_layout.addWidget(self.search_bar)
        self.add_button = QPushButton("Add picture")
        menu_layout.addWidget(self.add_button)

        gallery_layout = QGridLayout()

        main_layout.addLayout(menu_layout)
        main_layout.addLayout(gallery_layout, stretch=2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.add_button.clicked.connect(self.add_file)

    def add_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select the picture", "", "Images (*.png *.jpg)")

        if filepath:
            print(filepath)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoTaggingGallery()
    window.show()
    sys.exit(app.exec())