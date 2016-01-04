import rpc
import gevent
from gevent import GreenletExit
from gevent.pool import Group

class Master():

    def __init__(self, options):
        self.master_host = options.get('master_host')
        self.master_port = options.get('master_port')
        self.server = rpc.Server(self.master_host, self.master_port)
        self.greenlet = Group()
        self.greenlet.spawn(self.listener)
        return

    def listener(self):
        while True:
            msg = self.server.recv()
            if (msg):
                print "Got message: " + msg
