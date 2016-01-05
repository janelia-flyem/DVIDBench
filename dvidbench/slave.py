import uuid
import socket
import rpc
import gevent
import events
import random
import time
import sys
from gevent import GreenletExit
from gevent.pool import Group
from rpc import Message

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

runner = None

class Slave():

    def __init__(self, options):
        self.slave_id = socket.gethostname() + "_" + str(uuid.uuid1())
        self.master_host = options.master_host
        self.master_port = options.master_port
        self.client = rpc.Client(self.master_host, self.master_port)
        self.config = None
        self.workers = Group()

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
                print "starting {} workers".format(msg.data)
                self.start_workers(msg.data)

            elif msg.type == 'stop':
                print "stopping requests"

            else:
                print "Don't know what to do with message: {}".format(msg.type)

    def quit(self):
        # close down all the workers
        print "closing down workers"
        self.workers.kill(block=True)
        # message back to master?
        self.client.send(Message('client-quit', "i'm a gonner", self.identity))
        # exit
        exit(0)

    def worker(self):
       while True:
           url = random.choice(self.config.get('urls'))
           print "requesting url: {}".format(url)
           start = time.time()
           response_size = None
           try:
               data = urlopen(url).read()
               response_size = len(data)
           except Exception as e:
               print "unable to open {0}: {1}".format(url, e)

           end = time.time() - start
           print "fetching {0} took {1} ms".format(response_size, end * 1000)
           gevent.sleep(3)

    def start_workers(self,count):
        for i in range(count):
            print "starting worker {}".format(i)
            self.workers.spawn(self.worker)

