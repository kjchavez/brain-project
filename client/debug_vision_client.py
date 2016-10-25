import argparse
import cv2
import os
import socket
import time
import zmq

import api.vision_pb2

class DebugVisionClient(object):
    """ Sends each image from 'image_files' to the sensory endpoint. """
    def __init__(self, server_addr, image_files_iter):
        self.image_files_iter = image_files_iter
        context = zmq.Context()
        self.sock = context.socket(zmq.PUB)
        self.sock.connect(server_addr)

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
        data = cv2.imencode('.jpg', image)[1].tostring()

        perceived_image = api.vision_pb2.PerceivedImage()
        perceived_image.image.data = data
        perceived_image.image.encoding = "jpeg"
        perceived_image.timestamp.FromMilliseconds(int(time.time()*1000))
        perceived_image.source = "test"

        self.sock.send("image " + perceived_image.SerializeToString())

def isimage(filename):
    return filename.endswith('jpg')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--imagedir", default=None,
                        help="Directory of images to cycle through.")
    parser.add_argument("--hostname", default="jarvis.local")
    parser.add_argument("--port", type=int, default=9000)

    args = parser.parse_args()

    addr = "tcp://%s:%d" % (socket.gethostbyname(args.hostname), args.port)
    if args.imagedir:
        path = args.imagedir
        image_files = [os.path.join(path, f) for f in os.listdir(path) if
                       isimage(os.path.join(path, f))]

        client = DebugVisionClient(addr, iter(image_files))
    else:
        client = DebugVisionClient(addr, None)

    if args.imagedir is not None:
        print "Use an empty image filename to simply proceed to next image in",
        print args.imagedir

    while True:
        filename = raw_input("Enter image file: ")
        client.send_file(filename)

if __name__ == "__main__":
    main()

