import zmq.green as zmq
from communication import Socket

class Server(Socket):
    def __init__(self, host='*', port=4040):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://{0}:{1}".format(host, port))
        print "receiving messages on {0}:{1}".format(host, port)

        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://{0}:{1}".format(host, port + 1))
        print "sending messages on {0}:{1}".format(host, port + 1)
        return
