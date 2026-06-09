import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class AutoTaggingGallery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Tagging Gallery")
        self.resize(950, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoTaggingGallery()
    window.show()
    sys.exit(app.exec())