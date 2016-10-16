""" Server tasked with processing visual input from remote sensory sources. """
import cv2
import logging
import numpy as np
import zmq

import api.vision_pb2
from api.action_pb2 import Action
from vision.util import *
from action.emitter import ActionEmitter

# Constants that should be in cv2 but are MIA.
CV_LOAD_IMAGE_COLOR = 1

def create_bound_subcriber(address):
    """ Creates a SUB socket bound to 'address'. """
    context = zmq.Context()
    sock = context.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, '')
    sock.bind(address)
    return sock

class PerceivedImage(object):
    """ Wrapper for the PerceivedImage proto to provide richer behavior. 

    Useful properties:
    -----------------
    image:     Decoded, raw image representation
    timestamp: Datetime object representing when this image was perceived.
    source:    String indicating source of the image.

    """
    def __init__(self, data):
        perceived_image_proto = api.vision_pb2.PerceivedImage()
        perceived_image_proto.ParseFromString(data)
        self.timestamp = perceived_image_proto.timestamp.ToDatetime()
        self.source = perceived_image_proto.source

        # Save just the image data. We will lazily decode if the 'image'
        # property is accessed.
        self._image_data = perceived_image_proto.image.data
        self._image = None

    @property
    def image(self):
        if self._image is None:
            try:
                data = np.frombuffer(bytes(self._image_data), dtype=np.uint8)
                self._image = cv2.imdecode(data, CV_LOAD_IMAGE_COLOR)
            except:
                logging.warning("Failed to decode image")

        return self._image


class VisionHandler(object):
    def __init__(self, address):
        self.address = address
        self.emitter = None

    def handle(self, data):
        perceived_image = PerceivedImage(data)
        print "Received an image:"
        print perceived_image.image
        if self.emitter is not None:
            action = Action()
            action.display_text.text = "Received an image."
            self.emitter.send(action.SerializeToString())


    def start(self):
        self.sock = create_bound_subcriber(self.address)
        self.emitter = ActionEmitter.new_publisher()
        print_header("Running Vision Handler")
        while True:
            data = self.sock.recv()
            self.handle(data)

def main():
    handler = VisionHandler("tcp://0.0.0.0:5000")
    handler.start()

if __name__ == "__main__":
    main()

