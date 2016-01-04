import zmq.green as zmq
from communication import Socket

class Client(Socket):
    def __init__(self, host='*', port=4040):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://{0}:{1}".format(host, port + 1))

        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://{0}:{1}".format(host, port))
        return


