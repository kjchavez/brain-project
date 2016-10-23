from brain.services.stubs import ServiceStubs

def test_create_stubs():
    ServiceStubs.initialize(["brain/services/object_recognition/config.yaml"])
    assert ServiceStubs.get('object_recognition') is not None
