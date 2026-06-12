import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class Detector:
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path='efficientdet.tflite')
        options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
        self.detector = vision.ObjectDetector.create_from_options(options)

    def detect_tags(self, filepath):
        image = mp.Image.create_from_file(filepath)
        detection_result = self.detector.detect(image)
        tags = [category.category_name for detection in detection_result.detections
                for category in detection.categories]
        return tags
