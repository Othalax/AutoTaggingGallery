from ultralytics import YOLO

class Detector:
    def __init__(self):
        self.model = YOLO('yolov8n-cls.pt')

    def detect_tags(self, filepath):
        results = self.model(filepath)
        tags = []

        for result in results:
            if result.probs is not None:
                top5_indices = result.probs.top5
                top5_confidences = result.probs.top5conf

                for idx, conf in zip(top5_indices, top5_confidences):
                    if float(conf) > 0.3:
                        tag_name = result.names[idx]
                        clean_tag = tag_name.replace('_', ' ')
                        tags.append(clean_tag)

        return list(set(tags))