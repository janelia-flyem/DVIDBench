import uuid
import socket
import rpc
import gevent
from gevent import GreenletExit
from gevent.pool import Group

class Slave():

    def __init__(self, options):
        self.slave_id = socket.gethostname() + "_" + str(uuid.uuid1())
        self.master_host = options.get('master_host')
        self.master_port = options.get('master_port')
        self.client = rpc.Client(self.master_host, self.master_port)
        pass

    @property
    def identity(self):
        print self.slave_id
        return
