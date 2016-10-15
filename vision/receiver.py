""" Server tasked with processing visual input from remote sensory sources. """
import logging
import zmq
import cv2
import api.vision_pb2


def create_bound_subcriber(address):
    """ Creates a SUB socket bound to 'address'. """
    context = zmq.Context()
    sock = context.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, '')
    sock.bind(address)
    return sock

class PerceivedImage(object):
    """ Wrapper for the PerceivedImage proto to provide richer behavior. """
    def __init__(self, data):
        perceived_image_proto = api.vision_pb2.PerceivedImage()
        perceived_image_proto.ParseFromString(data)
        self.timestamp = perceived_image_proto.timestamp.ToDateTime()
        self.source = perceived_image_proto.source

        # Save just the image data. We will lazily decode if the 'image'
        # property is accessed.
        self._image_data = perceived_image_proto.image.data
        self._image = None

    @property
    def image(self):
        if self._image is None:
            try:
                self._image = cv2.imdecode(self._image_data)
            except:
                logging.warning("Failed to decode image")

        return self._image


class VisionHandler(object):
    def __init__(self, address):
        self.address = address

    def handle(self, data):
        perceived_image = PerceivedImage(data)
        print "Received an image:"
        print perceived_image.image

    def start(self):
        self.sock = create_bound_subcriber(self.address)
        while True:
            data = self.sock.recv_string()
            self.handle(data)

def main():
    handler = VisionHandler("tcp://0.0.0.0:5000")
    handler.start()

if __name__ == "__main__":
    main()

