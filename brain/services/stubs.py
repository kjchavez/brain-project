import logging
import sys
import socket
import yaml

from brain.services.service import ServiceStub

# Want to import all protos from the api, so that they may be configured by
# name in the configuration.
from api.vision_pb2 import *
from brain.services.service_api import *


def create_stub(config):
    if not all(config.has_key(key) for key in ('address', 'port',
        'request', 'response')):
        logging.critical("Service config must contain 'address',"
                         "'port', 'request', and 'response' fields.")
        return None

    try:
        RequestType = eval(config['request'])
    except:
        logging.critical("Request type not found in API: %s.",
                config['request'])
        return None
    try:
        ResponseType = eval(config['response'])
    except:
        logging.critical("Response type not found in API: %s.",
                config['response'])
        return None

    # Resolve the address to a raw ip address.
    addr = socket.gethostbyname(config['address'])
    port = int(config['port'])
    return ServiceStub("tcp://%s:%d" % (addr, port), RequestType, ResponseType)


class ServiceStubs(object):
    stubs = {}

    @staticmethod
    def initialize(service_configs):
        for config_file in service_configs:
            with open(config_file) as fp:
                config = yaml.load(fp)

            stub = create_stub(config)
            if stub is None:
                logging.error("Failed to create ServiceStub for %s",
                        config_file)

            ServiceStubs.stubs[config['name']] = stub

    @staticmethod
    def get(name):
        return ServiceStubs.stubs.get(name)

