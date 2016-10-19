""" Server tasked with processing visual input from remote sensory sources. """
import numpy as np

from brain.perception.vision.vision import PerceivedImage
from brain.thought_process import ThoughtProcess
import api.action_pb2


class ImageMemory(ThoughtProcess):
    def __init__(self, address, action_proxy_addr, sensory_output_addr):
        ThoughtProcess.__init__(self, "ImageMemory", address,
                                action_proxy_addr)
        self.add_input("image", sensory_output_addr, self.save_image,
                       topic="image")

    def save_image(self, data):
        perceived_image = PerceivedImage(data)
        print("Perceived an image with mean %f" %
              (np.mean(perceived_image.image),))

        action = api.action_pb2.Action()
        action.name = "Say"
        self.propose(action)

