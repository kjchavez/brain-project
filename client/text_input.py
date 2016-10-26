from client.pub_client import PublishClient

from api.text_pb2 import RawText

class TextInput(PublishClient):
    def __init__(self, hostname, port):
        PublishClient.__init__(self, hostname, port, "text")

    def send_text(self, text):
        raw_text = RawText()
        raw_text.text = text
        self.send_data(raw_text)

