from ultralytics import YOLO

class Detector:
    def __init__(self):
        self.model = YOLO('yolov8n-oiv7.pt')

    def detect_tags(self, filepath):
        results = self.model(filepath)
        tags = []

        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    conf = float(box.conf[0])

                    if conf > 0.3:
                        class_id = int(box.cls[0])
                        tag_name = result.names[class_id]

                        clean_tag = tag_name.replace('_', ' ')
                        tags.append(clean_tag)

        return list(set(tags))