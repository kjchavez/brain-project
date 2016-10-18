import argparse
import time
import logging
import yaml

from brain.perception.sensory_receiver import SensoryReceiver
from brain.perception.vision.receiver import ImageMemory


parser = argparse.ArgumentParser()
parser.add_argument("--config", default="brain/config.yaml")
args = parser.parse_args()

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


with open(args.config) as fp:
    config = yaml.load(fp)

receiver = SensoryReceiver(config['sensory_input_addr'],
                           config['sensory_output_addr'])

processes = [
    ImageMemory("inproc://image-memory",
                sensory_output_addr=config['sensory_output_addr']),
]

for p in processes:
    p.start()

while True:
    time.sleep(10)
    logging.debug("SensoryReceiver heartbeat.")
