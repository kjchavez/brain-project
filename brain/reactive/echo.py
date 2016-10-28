from brain.thought_process import ThoughtProcess

from api.text_pb2 import RawText
from brain.services.stubs import ServiceStubs
from brain.services.echo.api_pb2 import *

class EchoWords(ThoughtProcess):
    def __init__(self, address, action_proxy_addr, sensory_output_addr):
        ThoughtProcess.__init__(self, "EchoWords", address, action_proxy_addr)
        self.add_input("text", sensory_output_addr, self.echo, topic="text")

    def echo(self, data):
        rt = RawText()
        rt.ParseFromString(str(data))
        echo_fn = ServiceStubs.get("echo")
        request = EchoRequest()
        request.text = rt.text
        response = echo_fn(request)
        print "EchoResponse:", response
