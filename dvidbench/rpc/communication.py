from .protocol import Message

class Socket():
    def __init__(self):
        pass

    def send(self,msg):
        self.sender.send(msg.serialize())
        return

    def recv(self):
        data = self.receiver.recv()
        msg = Message.unserialize(data)
        return msg
