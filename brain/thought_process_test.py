from brain.thought_process import ThoughtProcess

import logging
import time
import zmq

def handler(data):
    print "Processing:", data

def smoke_test():
    tp = ThoughtProcess("test", "inproc://test-thoughts",
                        "inproc://action-proxy")
    tp.add_input("input", "inproc://test-input", handler)

    tp.start()

    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.PUB)
    sock.bind("inproc://test-input")
    sock.send("hello world")
    time.sleep(2)
    sock.close()
