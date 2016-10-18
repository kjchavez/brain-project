""" Server tasked with processing visual input from remote sensory sources. """
import numpy as np

from brain.perception.vision.vision import PerceivedImage
from brain.thought_process import ThoughtProcess


class ImageMemory(ThoughtProcess):
    def __init__(self, address, sensory_output_addr):
        ThoughtProcess.__init__(self, "ImageMemory", address)
        self.add_input("image", sensory_output_addr, self.save_image,
                       topic="image")

    def save_image(self, data):
        perceived_image = PerceivedImage(data)
        print("Perceived an image with mean %f" %
              (np.mean(perceived_image.image),))



"""
def create_bound_subcriber(address):
    context = zmq.Context()
    sock = context.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, '')
    sock.bind(address)
    return sock

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
"""
