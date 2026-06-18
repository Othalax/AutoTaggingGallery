# Auto Tagging Gallery

## Table of contents

- [Description](#description)
- [How to Use](#how-to-use)
- [Technologies](#technologies)
- [Installation and build](#installation-and-build)

  
## Description

Photo gallery that automatically detects objects in imported photos using the YOLOv8 AI model locally and tags them without user intervention. A toggle feature allows instant switching between the newest and oldest added photos. Double-clicking any photo opens its details, where generated tags are displayed as clickable links that can filter the main gallery. You can also filter the main gallery by searching for a tag using search bar.

## How to Use

1. Click the Add picture button and select one or multiple images. The button will indicate the processing state while the AI analyzes the photos in the background.
2. Double-click on any image, or right-click and select "Show details", to open the "Photo Details" window. Here you can see a higher-resolution version of the image, view its tags, and download a copy of the photo.
3. Type a keyword (for example 'cat') into the "Search by tag" bar at the top, or click on a blue tag link inside the "Photo Details" window.
4. Right-click image and select "Delete" to instantly remove the image from the grid, database, and local storage.
5. Right-click image and select "Copy to clipboard" to copy selected image.
6. Click the "Sort: Newest" or "Sort: Oldest" toggle button next to the search bar to change the display order.


## Technologies

Made using **Python 3.13**

Libraries:
- **PySide6** - https://doc.qt.io/qtforpython-6/
- **ultralytics** - https://docs.ultralytics.com/usage/python
- **pytest** - https://docs.pytest.org/en/stable/
- **PyInstaller** - https://pyinstaller.org/en/stable/

You can install all the dependencies by running

```pip install -r requirements.txt ```

## Installation and build

**Running the Application**  
To run the application from the source code, execute the main GUI script by typing: 

```python gui.py```

**Building the Executable**  
Alternatively, for a standalone experience, the application can be compiled into a executable file. The project includes a build script that automates this process using PyInstaller. The script bundles all dependencies, including AI models and the UI framework, into a standalone application. Once the process completes, the executable will be available in the generated 'dist' folder. To generate the .exe file, execute the following in your terminal:

```python build.py```

**Data Storage**  
By default, the application stores all user data in the OS-level AppData directory. The path is %APPDATA%/AutoTaggingGallery/. This includes gallery.db, the photos directory containing renamed image files, and the downloaded YOLO model.
