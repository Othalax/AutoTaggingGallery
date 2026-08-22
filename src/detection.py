from ultralytics import YOLO
import os
import configparser

class Detector:
    def __init__(self):
        appdata_dir = os.getenv('APPDATA')
        self.storage_dir = os.path.join(appdata_dir, "AutoTaggingGallery", 'yolov8n-oiv7.pt')
        self.model = YOLO(self.storage_dir)
        config = configparser.ConfigParser()
        config.read('../config.ini')
        self.confidence_threshold = float(config['Detector']['confidence_threshold'])

    def detect_tags(self, filepath):
        results = self.model(filepath)
        tags = []

        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    conf = float(box.conf[0])

                    if conf > self.confidence_threshold:
                        class_id = int(box.cls[0])
                        tag_name = result.names[class_id]

                        clean_tag = tag_name.replace('_', ' ')
                        tags.append(clean_tag)

        return list(set(tags))