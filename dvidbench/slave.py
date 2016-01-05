import uuid
import socket
import rpc
import gevent
from gevent import GreenletExit
from gevent.pool import Group
from rpc import Message

class Slave():

    def __init__(self, options):
        self.slave_id = socket.gethostname() + "_" + str(uuid.uuid1())
        self.master_host = options.master_host
        self.master_port = options.master_port
        self.client = rpc.Client(self.master_host, self.master_port)

        print "sent message to {0}:{1}".format(self.master_host, self.master_port)
        self.client.send(Message('client-started','greetings master',self.identity))
        pass

    @property
    def identity(self):
        print self.slave_id
        return

    def listener(self):
        while True:
            msg = self.client.recv()
            if msg.type == 'config':
                print "got configuration from master"
                print msg.data.get('urls')
            elif msg.type == 'quit':
                print msg.data
