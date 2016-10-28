import argparse
import glob
import logging
import os
import time
import yaml

from brain.perception.sensory_receiver import SensoryReceiver
from brain.perception.vision.receiver import ImageMemory
from brain.reactive.echo import EchoWords
from brain.services.stubs import ServiceStubs


parser = argparse.ArgumentParser()
parser.add_argument("--config", default="brain/config.yaml")
parser.add_argument("--services_dir", default="brain/services")
args = parser.parse_args()

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


# Wire up all the stubs for the Services
service_configs = glob.glob(os.path.join(args.services_dir, "*/config.yaml"))
ServiceStubs.initialize(service_configs)

with open(args.config) as fp:
    config = yaml.load(fp)

receiver = SensoryReceiver(config['sensory_input_addr'],
                           config['sensory_output_addr'])

processes = [
    ImageMemory("inproc://image-memory", config['action_directive_proxy'],
                sensory_output_addr=config['sensory_output_addr']),
    EchoWords("inproc://echo-words", config['action_directive_proxy'],
              sensory_output_addr=config['sensory_output_addr'])
]

for p in processes:
    p.start()

while True:
    time.sleep(10)
    logging.debug("SensoryReceiver heartbeat.")
