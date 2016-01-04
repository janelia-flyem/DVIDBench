class Socket():
    def __init__(self):
        pass

    def send(self,msg):
        print "sent {}".format(msg)
        self.sender.send(msg)
        return

    def recv(self):
        msg = self.receiver.recv()
        print msg
        return
