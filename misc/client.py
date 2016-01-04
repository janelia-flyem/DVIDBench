import zmq.green as zmq
import msgpack
import time

context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://127.0.0.1:3000")

sender = context.socket(zmq.PUSH)
sender.connect("tcp://127.0.0.1:3001")
workers = 0

def serialize(msg):
    return msgpack.dumps(msg)

def unserialize(msg):
    return msgpack.loads(msg)

def send(msg):
    sender.send(serialize(msg))

def recv():
    print "checking for messages"
    data = receiver.recv()
    return unserialize(data)

while True:
    global workers
    msg = recv()
    if msg == 'spawn':
        workers += 1
        print "spawning a new worker {}".format(workers)
    elif msg == 'kill':
        workers -= 1
        print "killing a worker {}".format(workers)
    else:
        print msg
