from brain.thought_process import ThoughtProcess

import logging
import time
import zmq

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

def handler(data):
    print "Processing:", data

tp = ThoughtProcess("test", "inproc://test-thoughts")
tp.add_input("input", "inproc://test-input", handler)

tp.start()

ctx = zmq.Context.instance()
sock = ctx.socket(zmq.PUB)
sock.bind("inproc://test-input")
sock.send("hello world")
time.sleep(2)
sock.close()
