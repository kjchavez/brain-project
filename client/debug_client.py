import argparse
from cmd import Cmd

from client.text_input import TextInput
from client.debug_vision_client import DebugVisionClient

class DebugClientShell(Cmd):
    def __init__(self, text_client, image_client):
        Cmd.__init__(self)
        self.text_client = text_client
        self.image_client = image_client

    def do_text(self, args):
        """ Sends text as stimulus to server. """
        self.text_client.send_text(args)
        print "Sent \"%s\"." % args

    def do_image(self, args):
        """ Sends picture from 'filename' to server as PerceivedImage. """
        self.image_client.send_file(args)
        print "Sent [image:%s] to server" % args

    def do_quit(self, args):
        print "Exiting."
        raise SystemExit

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", help="Hostname of server")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--imagedir", type=str, default=None,
                        help="Path to directory of images to use by default.")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()

    # Create individual client modules.
    text_client = TextInput(args.hostname, args.port)
    image_client = DebugVisionClient(args.hostname, args.port, args.imagedir)

    shell = DebugClientShell(text_client=text_client,
                             image_client=image_client)
    shell.prompt = ">> "
    shell.cmdloop()
