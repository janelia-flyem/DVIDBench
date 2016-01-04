import zmq.green as zmq
import msgpack
import time
import random

context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://127.0.0.1:3001")

sender = context.socket(zmq.PUSH)
sender.bind("tcp://127.0.0.1:3000")

def serialize(msg):
    return msgpack.dumps(msg)

def unserialize(msg):
    return msgpack.loads(data)

def send(msg):
    sender.send(serialize(msg))
    print "sent message"

def recv():
    data = receiver.recv()
    return unserialize(data)

while True:
    messages = ['wibble','spawn','spawn','spawn','spawn','spawn','spawn','kill']
    send(random.choice(messages))
    time.sleep(1)
