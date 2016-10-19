import logging
import threading
import zmq

import api.action_pb2

class Action(object):
    def __init__(self, serialized_proto):
        self.action_proto = api.action_pb2.Action()
        self.action_proto.ParseFromString(serialized_proto)

    @property
    def type(self):
        return self.action_proto.WhichOneOf("action_type")

    @property
    def name(self):
        return self.action_proto.name


def propose(action_proto, proxy_addr):
    context = zmq.Context.instance()
    sock = context.socket(zmq.PUSH)
    sock.connect(proxy_addr)
    sock.send(action_proto.SerializeToString())
    sock.close()


class BasalGanglia(object):
    """ Listens for incoming action proposals and decides which should be
        executed.
    """
    def __init__(self, proxy_addr):
        t = threading.Thread(target=self.run, args=(proxy_addr,))
        t.daemon = True
        t.start()

    def should_accept(self, action):
        """ Returns true if this action should be executed. """
        return True

    def run(self, proxy_addr):
        context = zmq.Context.instance()
        input_sock = context.socket(zmq.PULL)
        input_sock.bind(proxy_addr)
        while True:
            data = input_sock.recv()
            action = Action(data)
            if self.should_accept(action):
                logging.info("Executing action [%s]...", action.name)

