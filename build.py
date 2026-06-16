import PyInstaller.__main__


def build_app():

    PyInstaller.__main__.run([
        'gui.py',
        '--name=AutoTaggingGallery',
        '--windowed',
        '--collect-all=ultralytics',
        '--hidden-import=PySide6',
        '--clean',
        '-y'
    ])

if __name__ == "__main__":
    build_app()