import argparse
import time
import logging
import yaml

from brain.action.basal_ganglia import BasalGanglia


parser = argparse.ArgumentParser()
parser.add_argument("--config", default="brain/config.yaml")
args = parser.parse_args()

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


with open(args.config) as fp:
    config = yaml.load(fp)

basal_ganglia = BasalGanglia(config['action_directive_proxy'])

while True:
    time.sleep(10)
    logging.debug("BasalGanglia heartbeat.")
