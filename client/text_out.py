""" A lightweight node that can produce text output. """

import socket
import zmq
from api.action_pb2 import Action

def display_text(action):
    if action.HasField('display_text'):
        print ">>>", action.display_text.text

def create_connected_subscriber(address):
    context = zmq.Context.instance()
    sock = context.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, '')
    sock.connect(address)
    return sock


class ActionHandler(object):
    def __init__(self, source_addr, execute_fn):
        self.source_addr = source_addr
        self.execute_fn = execute_fn

    def run(self):
        sock = create_connected_subscriber(self.source_addr)
        while True:
            data = sock.recv()
            action = Action()
            action.ParseFromString(data)
            self.execute_fn(action)

def main():
    ip = socket.gethostbyname('jarvis.local')
    address = "tcp://%s:5001" % ip
    handler = ActionHandler(address, display_text)
    handler.run()

if __name__ == "__main__":
    main()

