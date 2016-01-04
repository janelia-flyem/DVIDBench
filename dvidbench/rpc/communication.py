from .protocol import Message

class Socket():
    def __init__(self):
        pass

    def send(self,msg):
        print "sent {}".format(msg.data)
        self.sender.send(msg.serialize())
        return

    def recv(self):
        data = self.receiver.recv()
        msg = Message.unserialize(data)
        return msg
