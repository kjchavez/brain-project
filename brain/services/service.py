""" Abstract base class for a service within brain. """

import logging
import threading
import uuid
import zmq


class ServiceStub(object):
    def __init__(self, addr, RequestType, ResponseType):
        self.addr = addr
        self.RequestType = RequestType
        self.ResponseType = ResponseType

    def call(self, request):
        if not isinstance(request, self.RequestType):
            logging.error("Invalid request type.")

            # Should we return None or empty response?
            return None

        context = zmq.Context.instance()
        sock = context.socket(zmq.REQ)
        sock.connect(self.addr)

        logging.debug("Issuing request:\n%s", request)
        sock.send(request.SerializeToString())
        response = self.ResponseType()
        response.ParseFromString(sock.recv())
        logging.debug("Received response:\n%s", response)

        sock.close()
        return response

    def __call__(self, request):
        return self.call(request)


class Service(object):
    def __init__(self, addr, RequestType, ResponseType, handler_fn,
                 num_handlers=1):
        self.addr = addr
        self.backend_addr = "inproc://%s" % uuid.uuid4()
        self.handler_fn = handler_fn
        self.RequestType = RequestType
        self.ResponseType = ResponseType

        # Start up N handlers.
        for _ in xrange(num_handlers):
            t = threading.Thread(target=self.run_handler)
            t.daemon = True
            t.start()

    def start(self):
        # Fire up the router-dealer mechanism.
        t = threading.Thread(target=self.run_router_dealer)
        t.daemon = True
        t.start()

    def run(self):
        logging.info("Starting service [${name}] at %s.", self.addr)
        self.run_router_dealer()

    def run_router_dealer(self):
        context = zmq.Context.instance()
        frontend = context.socket(zmq.ROUTER)
        backend = context.socket(zmq.DEALER)
        frontend.bind(self.addr)
        backend.bind(self.backend_addr)

        # Initialize poll set
        poller = zmq.Poller()
        poller.register(frontend, zmq.POLLIN)
        poller.register(backend, zmq.POLLIN)

        # Switch messages between sockets
        while True:
            socks = dict(poller.poll())

            if socks.get(frontend) == zmq.POLLIN:
                backend.send_multipart(frontend.recv_multipart())

            if socks.get(backend) == zmq.POLLIN:
                frontend.send_multipart(backend.recv_multipart())

    def run_handler(self):
        context = zmq.Context.instance()
        sock = context.socket(zmq.REP)
        sock.connect(self.backend_addr)
        while True:
            data = sock.recv()
            request = self.RequestType()
            request.ParseFromString(data)
            response = self.handler_fn(request)
            if not isinstance(response, self.ResponseType):
                logging.warning("Invalid response type.")
                response = self.ResponseType()
            sock.send(response.SerializeToString())
