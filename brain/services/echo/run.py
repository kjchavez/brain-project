import argparse
import logging
import yaml

from brain.services.service import Service
from .api_pb2 import *

parser = argparse.ArgumentParser()
parser.add_argument("--config",
                    default="brain/services/echo/config.yaml")
parser.add_argument("--loglevel", choices=["debug", "info", "warning",
                    "error"], default="info")
args = parser.parse_args()

level = getattr(logging, args.loglevel.upper(), None)
logging.basicConfig(level=level)

with open(args.config) as fp:
    config = yaml.load(fp)

def echo(request):
    response = EchoResponse()
    response.text = request.text
    return response

service = Service("tcp://0.0.0.0:%d" % config['port'], EchoRequest,
                  EchoResponse, echo, num_handlers=1)

service.run()
