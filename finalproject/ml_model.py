import os
import json
import tensorflow as tf
from PIL import Image
import numpy as np

EXPORT_MODEL_VERSION = 1

class TFModel:
    def __init__(self, model_dir) -> None:
        
        self.model_dir = model_dir
        with open(os.path.join(model_dir, "signature.json"), "r") as f:
            self.signature = json.load(f)
        self.model_file = model_dir+self.signature.get("filename")
        if not os.path.isfile(self.model_file):
            raise FileNotFoundError(f"Model file does not exist")
        self.inputs = self.signature.get("inputs")
        self.outputs = self.signature.get("outputs")
        
        self.session = None

       
        version = self.signature.get("export_model_version")
        if version is None or version != EXPORT_MODEL_VERSION:
            print(
                f"There has been a change to the model format. Please use a model with a signature 'export_model_version' that matches {EXPORT_MODEL_VERSION}."
            )

    def load(self) -> None:
        self.cleanup()
       
        self.session = tf.compat.v1.Session(graph=tf.Graph())
        
        tf.compat.v1.saved_model.loader.load(sess=self.session, tags=self.signature.get("tags"), export_dir=self.model_dir)

    def predict(self, image: Image.Image) -> dict:
        
        if self.session is None:
            self.load()

        image = self.process_image(image, self.inputs.get("Image").get("shape"))
        
        feed_dict = {self.inputs["Image"]["name"]: [image]}

        
        fetches = [(key, output["name"]) for key, output in self.outputs.items()]

        
        outputs = self.session.run(fetches=[name for _, name in fetches], feed_dict=feed_dict)
        return self.process_output(fetches, outputs)

    def process_image(self, image, input_shape) -> np.ndarray:
        """
        Given a PIL Image, center square crop and resize to fit the expected model input, and convert from [0,255] to [0,1] values.
        """
        width, height = image.size
        
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        if width != height:
            square_size = min(width, height)
            left = (width - square_size) / 2
            top = (height - square_size) / 2
            right = (width + square_size) / 2
            bottom = (height + square_size) / 2
            
            image = image.crop((left, top, right, bottom))
        
        input_width, input_height = input_shape[1:3]
        if image.width != input_width or image.height != input_height:
            image = image.resize((input_width, input_height))

        
        image = np.asarray(image) / 255.0
        
        return image.astype(np.float32)

    def process_output(self, fetches, outputs) -> dict:
        
        out_keys = ["label", "confidence"]
        results = {}
        
        for i, (key, _) in enumerate(fetches):
            val = outputs[i].tolist()[0]
            if isinstance(val, bytes):
                val = val.decode()
            results[key] = val
        confs = results["Confidences"]
        labels = self.signature.get("classes").get("Label")
        output = [dict(zip(out_keys, group)) for group in zip(labels, confs)]
        sorted_output = {"predictions": sorted(output, key=lambda k: k["confidence"], reverse=True)}
        return sorted_output

    def cleanup(self) -> None:
        
        if self.session is not None:
            self.session.close()
            self.session = None

    def __del__(self) -> None:
        self.cleanup()