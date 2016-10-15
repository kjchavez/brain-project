import sys
import copy
import io
import time
import threading
import cv2
import argparse

import api.vision_pb2


parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0)

args = parser.parse_args()

class AsyncVideoCapture(object):
    def __init__(self, device):
        self.device = device
        self.lock = threading.Lock()
        self.image = None

    def run(self):
        video_capture = cv2.VideoCapture(args.device)
        if not video_capture.isOpened():
            print "Failed to open video capture device."
            sys.exit(1)

        while True:
            ret, image = video_capture.read()
            if not ret:
                print "Failed to capture image"
                continue

            self.lock.acquire()
            self.image = image
            self.lock.release()

    def read(self):
        self.lock.acquire()
        image = copy.deepcopy(self.image)
        self.lock.release()
        return image

video_capture = AsyncVideoCapture(args.device)
t = threading.Thread(target=video_capture.run)
t.daemon = True
t.start()

def get_encoded_image():
    image = video_capture.read()
    try:
        encoded = cv2.imencode('.jpg', image)[1].tostring()
        return encoded
    except:
        return None

def get_perceived_image():
    data = get_encoded_image()
    if data is None:
        return None

    perceived_image = api.vision_pb2.PerceivedImage()
    perceived_image.image.data = data
    perceived_image.image.encoding = "jpeg"
    perceived_image.timestamp.FromMilliseconds(int(time.time()*1000))
    perceived_image.source = "test"
    return perceived_image

def main():
    while True:
        time.sleep(1.0)
        perceived_image = get_perceived_image()
        print perceived_image

if __name__ == "__main__":
    main()
