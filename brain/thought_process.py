import logging
import threading
import uuid
import zmq

import brain.action.basal_ganglia

class ThoughtProcess(object):
    """ Abstract base class for processes that integrate signals over time and
    publish new ephemeral signals. These can be thought of as creating
    higher-level abstractions over low-level signals.
    """
    def __init__(self, name, address, action_proxy_addr):
        """
        Args:
            address: fixed address where signals are published
        """
        self.name = name
        self.output_address = address

        # Functions to be invoked with the data received on each of the named
        # inputs.
        self.handlers = {}

        # Dictionary of named input addresses
        self.input_addresses = {}

        self.proxy_pub_address = "inproc://%s" % (str(uuid.uuid4()),)
        self.action_proxy_addr = action_proxy_addr

    def handle_input_signal(self, data):
        raise NotImplementedError("Handler not implemented.")

    def add_input(self, name, source_addr, handler, topic=""):
        self.input_addresses[name] = (source_addr, topic)
        self.handlers[name] = handler
        # TODO: Signal the running loop to add a new socket!

    def propose(self, action_proto):
        logging.debug("Proposing action:\n%s", action_proto)
        brain.action.basal_ganglia.propose(action_proto, self.action_proxy_addr)

    def publish(self, signal, topic=None):
        context = zmq.Context.instance()
        sock = context.socket(zmq.PAIR)
        sock.connect(self.proxy_pub_address)
        sock.send(signal)
        sock.close()

    def start(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()

    def run(self):
        context = zmq.Context.instance()

        # Map of socket object to name
        input_sockets = {}
        for name, (address, topic) in self.input_addresses.items():
            sock = context.socket(zmq.SUB)
            sock.setsockopt(zmq.SUBSCRIBE, topic)
            sock.connect(address)
            input_sockets[sock] = (name, topic)

        # Create an output socket for this node.
        output_socket = context.socket(zmq.PUB)
        output_socket.bind(self.output_address)

        # Create a proxy receiver for publishing signals from other threads.
        proxy_socket = context.socket(zmq.PAIR)
        proxy_socket.bind(self.proxy_pub_address)

        # Polling mechanism.
        poller = zmq.Poller()
        poller.register(proxy_socket, zmq.POLLIN)
        for sock in input_sockets:
            poller.register(sock, zmq.POLLIN)

        while True:
            socks = dict(poller.poll())
            for sock in socks:
                if sock == proxy_socket:
                    # Forward the signal
                    logging.debug("Forwarding published signal to [%s].",
                                  self.output_address)
                    output_socket.send(sock.recv())

                if socks[sock] == zmq.POLLIN:
                    input_name, topic = input_sockets[sock]

                    # Find the specialized handler, or fall back to the generic
                    # input signal handler
                    handler = self.handlers.get(input_name,
                                                self.handle_input_signal)
                    logging.debug("ThoughtProcess:%s received input from "
                                  "[%s].", self.name, input_name)
                    data = sock.recv()
                    if topic:
                        data = data.split(" ", 1)[-1]

                    # Run the handler in a separate thread so we aren't
                    # concerned with blocking behavior.
                    #
                    # TODO: We might want to put a cap on the number of
                    # simultaneously active threads.
                    t = threading.Thread(target=handler, args=(data,))
                    t.daemon = True
                    t.start()

