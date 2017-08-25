import argparse
import zmq


# receiver
context = zmq.Context()
socket0 = context.socket(zmq.REP)
socket0.bind('tcp://127.0.0.1:5555')

while True:
    msg = socket0.recv()
    print(msg)
    socket0.send_string("go fuck urself" + str(msg))
   