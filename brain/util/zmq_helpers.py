import threading
import zmq

class Forwarder(object):
    """ Sets up to bound addresses and forwards from a SUBSCRIBER @
    input_address to a PUBLISHER @ output_address.
    """
    def __init__(self, input_address, output_address):
        t = threading.Thread(target=self.run, args=(input_address,
                                                    output_address))
        t.daemon = True
        t.start()

    def run(self, input_address, output_address):
        context = zmq.Context.instance()
        self.pub_sock = context.socket(zmq.PUB)
        self.pub_sock.bind(output_address)

        self.sub_sock = context.socket(zmq.SUB)
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "")
        self.sub_sock.bind(input_address)

        zmq.device(zmq.FORWARDER, self.sub_sock, self.pub_sock)

    def __del__(self):
        self.sub_sock.close()
        self.pub_sock.close()
