from brain.services.service import ServiceStub

stubs = {
    "object_recognition": None  # Should really be ServiceStub.
}

def get(name):
    return stubs[name]
