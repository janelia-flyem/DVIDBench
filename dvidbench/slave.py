import uuid
import socket
import rpc
import gevent
import events
import random
import time
import sys
import requests
from gevent import GreenletExit
from gevent.pool import Group
from rpc import Message

STATS_REPORT_INTERVAL = 3

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
        self.session = requests.Session()
        self.min_wait = 1000
        self.max_wait = 1000
        self.stats = {
            'workers': 0
        }

        print "sent message to {0}:{1}".format(self.master_host, self.master_port)
        self.client.send(Message('client-started','greetings to master',self.identity))

        self.workers.spawn(self.stats_reporter)
        return

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
           stats = {}

           start = time.time()

           response = self.session.get(url)

           stats['duration'] = (time.time() - start) * 1000
           stats['content_size'] = len(response.content)
           stats['status_code'] = response.status_code

           self.client.send(Message("stats", stats, self.identity))

           millis = random.randint(self.min_wait, self.max_wait)
           seconds = millis / 1000.0
           gevent.sleep(seconds)

    def start_workers(self,count):
        for i in range(count):
            print "starting worker {}".format(i)
            self.workers.spawn(self.worker)
        self.stats['workers'] += count;

    def stats_reporter(self):
        while True:
            # TDOD: fetch data for stats reporting
            self.client.send(Message('stats', self.stats, self.identity))
            gevent.sleep(STATS_REPORT_INTERVAL)

