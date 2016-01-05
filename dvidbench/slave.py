import uuid
import socket
import rpc
import gevent
import events
from gevent import GreenletExit
from gevent.pool import Group
from rpc import Message

class Slave():

    def __init__(self, options):
        self.slave_id = socket.gethostname() + "_" + str(uuid.uuid1())
        self.master_host = options.master_host
        self.master_port = options.master_port
        self.client = rpc.Client(self.master_host, self.master_port)
        self.config = None

        print "sent message to {0}:{1}".format(self.master_host, self.master_port)
        self.client.send(Message('client-started','greetings master',self.identity))
        pass

    @property
    def identity(self):
        return self.slave_id

    def listener(self):
        while True:
            msg = self.client.recv()
            if msg.type == 'config':
                print "got configuration from master"
                self.config = msg.data

            elif msg.type == 'quit':
                print "shutting down client: {}".format(self.identity)
                self.quit()

            elif msg.type == 'start':
                print "starting requests"

            elif msg.type == 'stop':
                print "stopping requests"

            else:
                print "Don't know what to do with message: {}".format(msg.type)

    def quit(self):
        # close down all the workers
        print "closing down workers"
        # message back to master?
        self.client.send(Message('client-quit', "i'm a gonner", self.identity))
        # exit
        exit(0)
