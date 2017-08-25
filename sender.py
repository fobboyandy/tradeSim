import argparse
import zmq
import time

# client
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://127.0.0.1:5555')
socket.send_string("hello\n")
msg = socket.recv()