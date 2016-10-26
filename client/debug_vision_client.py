import argparse
import cv2
import os
import socket
import time
import zmq

from client.pub_client import PublishClient
import api.vision_pb2

def isimage(filename):
    return filename.endswith('jpg')

class DebugVisionClient(PublishClient):
    def __init__(self, hostname, port, imagedir=None):
        PublishClient.__init__(self, hostname, port, "image")
        if imagedir is not None:
            image_files = [os.path.join(imagedir, f) for f in
                           os.listdir(imagedir) if
                           isimage(os.path.join(imagedir, f))]

            self.image_files_iter = iter(image_files)
        else:
            self.image_files_iter = None

    def send_file(self, image_file):
        if not image_file and self.image_files_iter is None:
            print "Must either specify image file iterator or an explicit ",
            print "image file at runtime."
            return

        if not image_file:
            try:
                image_file = next(self.image_files_iter)
                print "Sending %s." % image_file
            except:
                print "Reached end of image files iterator."
                return

        image = cv2.imread(image_file, 1)
        if image is None:
            print "Failed to read image."
            return

        data = cv2.imencode('.jpg', image)[1].tostring()

        perceived_image = api.vision_pb2.PerceivedImage()
        perceived_image.image.data = data
        perceived_image.image.encoding = "jpeg"
        perceived_image.timestamp.FromMilliseconds(int(time.time()*1000))
        perceived_image.source = "test"

        self.send_data(perceived_image)

