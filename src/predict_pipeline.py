"""
Predict Pipeline:
Classes
- Predict Pipeline
    1. Load model and create output images
    2. Write images to static/ and GCS 
- CustomData
    1. Gets image objects from tmp/
"""
import os
import sys
import shutil
import torch
from PIL import Image, ImageDraw
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
from src.exception import CustomException

class CustomData:
    """
    From the tmp directory path, creates a list of image objects
    to be passed to the predict pipeline.
    """
    def __init__(self, tmp_path):
        """
        Creates a list of the image file paths
        """
        self.image_paths = list()
        for tmp_dir, _, images in os.walk(tmp_path):
            for img in images:
                single_image_path = os.path.join(tmp_dir, img)
                self.image_paths.append(single_image_path)

    def get_data(self):
        """
        From the list of image paths, returns a list 
        of image objects
        """
        try:
            images = [Image.open(img).convert('RGB') for img in self.image_paths]

            return images 
        
        except Exception as e:
            raise CustomException(e, sys)

class PredictPipeline:
    """
    Class with methods to process the raw images and 
    generate the output images and results 
    """
    def __init__(self):
        self.check_point = "google/owlv2-base-patch16-ensemble"
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.check_point)
        self.processor = AutoProcessor.from_pretrained(self.check_point)


    def predict(self, images, image_paths):
        """
        From a list of image objects, returns the images with
        bounding boxes and object detection results
        """
        try:
            queries = ['solar panel', 'pool']
            inputs = self.processor(text=queries, images=images, return_tensors='pt')

            with torch.no_grad():
                outputs = self.model(**inputs)
                target_sizes = torch.tensor([img.size[::-1] for img in images])
                results = self.processor.post_process_object_detection(
                    outputs, 
                    threshold=0.3,
                    target_sizes=target_sizes
                )

            # Draw bounding boxes
            for idx, img in enumerate(images):
                draw = ImageDraw.Draw(img)

                scores = results[idx]['scores'].tolist()
                labels = results[idx]['labels'].tolist()
                boxes = results[idx]['boxes'].tolist()

                for box, score, label in zip(boxes, scores, labels):
                    xmin, ymin, xmax, ymax = box
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="#39ff14", width=2)
                    draw.text((xmin, ymin), f"{queries[label]}: {round(score,2)}", fill="white")

            #os.makedirs('static/', exist_ok=True)
            #for idx, img in enumerate(images):
            #    file_name = image_paths[idx].split('/')[-1]
            #    img.save(f'static/{file_name}')

            shutil.rmtree('tmp')

            return images, results

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == '__main__':
    tmp_path = 'tmp'
    data_obj = CustomData(tmp_path)
    images = data_obj.get_data()

    pred_pipe = PredictPipeline()
    out_imgs, results = pred_pipe.predict(images, data_obj.image_paths)