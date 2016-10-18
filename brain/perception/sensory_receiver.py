from brain.util.zmq_helpers import Forwarder

class SensoryReceiver(Forwarder):
    """ Central node that receives all external sensory input and forwards to
    internal network.
    """
    def __init__(self, input_address, output_address):
        Forwarder.__init__(self, input_address, output_address)
