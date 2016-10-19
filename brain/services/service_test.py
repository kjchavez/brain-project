from brain.services.service import Service
from brain.services.service import ServiceStub

class FakeProto:
    def __init__(self, string=""):
        self.string = string

    def ParseFromString(self, string):
        self.string = string

    def SerializeToString(self):
        return self.string

    def __str__(self):
        return "FakeProto { value: %s }" % self.string

def fake_handler(request):
    response = FakeProto(request.string + " response")
    return response

service = Service("inproc://test", FakeProto, FakeProto, fake_handler)
stub = ServiceStub("inproc://test", FakeProto, FakeProto)

response = stub(FakeProto("test request"))
print response
