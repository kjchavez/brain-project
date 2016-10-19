import argparse
import yaml

from brain.services.service import Service
from brain.services.object_recognition.recognition import ObjectRecognizer
from brain.services.object_recognition.api_pb2 import RecognizedObjects
from api.vision_pb2 import Image

parser = argparse.ArgumentParser()
parser.add_argument("--config",
                    default="brain/services/object_recognition/config.yaml")
args = parser.parse_args()

with open(args.config) as fp:
    config = yaml.load(fp)

recognizer = ObjectRecognizer(config['graph_def_file'],
                              config['label_lookup_path'],
                              config['uid_lookup_path'])

def recognize(image):
    top5 = recognizer.recognize(image.data, num_top_predictions=5)
    recognized_objects = RecognizedObjects()
    for obj in top5:
        recognized_objects.object.add(name=obj)

    return recognized_objects

service = Service("tcp://0.0.0.0:%d" % config['port'], Image,
                  RecognizedObjects, recognizer.recognize, num_handlers=1)

service.run()
