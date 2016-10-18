import cv2
import logging
import numpy as np

import api.vision_pb2

# Constants that should be in cv2 but are MIA.
CV_LOAD_IMAGE_COLOR = 1

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

