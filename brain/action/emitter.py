import threading
import zmq


class ActionEmitter(object):
    FRONTEND_ADDRESS = "tcp://0.0.0.0:5001"
    BACKEND_ADDRESS = "inproc://action_emit_proxy"
    instance = None
    def __init__(self, address):
        t = threading.Thread(target=self.run, args=(address,))
        t.daemon = True
        t.start()

    def run(self, address):
        context = zmq.Context.instance()
        pub_sock = context.socket(zmq.PUB)
        pub_sock.bind(address)
        sub_sock = context.socket(zmq.SUB)
        sub_sock.setsockopt(zmq.SUBSCRIBE, "")
        sub_sock.bind(ActionEmitter.BACKEND_ADDRESS)
        zmq.device(zmq.FORWARDER, pub_sock, sub_sock)

    @staticmethod
    def new_publisher():
        if ActionEmitter.instance is None:
            ActionEmitter.instance = \
                    ActionEmitter(ActionEmitter.FRONTEND_ADDRESS)

        context = zmq.Context.instance()
        sock = context.socket(zmq.PUB)
        sock.connect(ActionEmitter.BACKEND_ADDRESS)
        return sock

