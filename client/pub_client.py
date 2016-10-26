import socket
import zmq

class PublishClient(object):
    def __init__(self, hostname, port, topic):
        server_addr = "tcp://%s:%d" % (socket.gethostbyname(hostname), port)
        context = zmq.Context.instance()
        self.sock = context.socket(zmq.PUB)
        self.sock.connect(server_addr)
        self.topic = topic

    def send_data(self, data):
        """ Publishes data with the client's topic.

        Args:
            data: Must either be a string or provide a SerializeToString()
                  method.
        """
        if not isinstance(data, str):
            data = data.SerializeToString()

        self.sock.send("%s " + data)
