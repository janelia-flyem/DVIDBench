import uuid
import socket
import rpc
import gevent
import events
import random
import time
import datetime
import sys
import requests
from gevent import GreenletExit
from gevent.pool import Group
from rpc import Message
from stats import global_stats
from requests.exceptions import (RequestException, MissingSchema, InvalidSchema, InvalidURL)

STATS_REPORT_INTERVAL = 3
SLOW_REQUEST_THRESHOLD = 100 #ms

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
        self.stats = global_stats
        self.worker_count = 0
        self.debug = options.debug

        self.client.send(Message('client-started','greetings to master',self.identity))

        # placing stats reporter in its own group, so it doesn't get killed
        # with the workers.
        self.reporter = Group().spawn(self.stats_reporter)
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
                self.stop_workers(msg.data)

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
           #url = random.choice(self.config.get('urls'))

           #x = random.choice(range(27,85))
           #y = random.choice(range(1540,1694))
           #x = 35
           #y = 1673

           # tem-dvid server
           url = ("http://10.40.3.163:8000/api/node/b030517ccbe5417b9766a03133149adc/v9.1.512x512.jpg/tile/xy/1/152_{0}_{1}".format(x, y))

           # this is a node server running from ~/work/javascript
           #url = ("http://tem-dvid:8080/api/node/b030517ccbe5417b9766a03133149adc/v9.1.512x512.jpg/tile/xy/1/152_{0}_{1}".format(x, y))

           # url = "http://tem-dvid:9000/kvautobus/api/keyvalue_range/AQAAAAUDAgABAAAAAQOAAAaJgAAAI4AAAJgAAAAAAAAAAAA=/AQAAAAUDAgABAAAAAQOAAAaJgAAAI4AAAJj___________8=/"
           # url = "http://tem-dvid:7400/api/node/0c8bc973dba74729880dd1bdfd8d0c5e/grayscale/raw/xy/512_512/7680_5632_4"

           #x = random.choice(range(29,35))
           #z = random.choice(range(4398, 4498))
           #url = ('http://goinac-ws1/data/catmaid-tiles/v9.1-xy/2/{0}/15/{1}.png'.format(z,x))

           # steve's google url
           #url = "http://104.197.207.55:8000/api/node/558ccd3f312e4c8d8afce495809c26fb/tiles/tile/xy/0/0_0_0"

           stats = {}
           if self.debug:
               print "[{0}] requesting url: {1}".format(datetime.datetime.now(), url)

           start = time.time()

           try:
               response = self.session.get(url)
           #capture connection errors when the remote is down.
           except RequestException as e:
               events.request_failure.fire(
                   request_type = 'GET',
                   name = url,
                   response_time = 0,
                   exception = e
               )
           else:
               stats['duration'] = int((time.time() - start) * 1000)
               stats['content_size'] = len(response.content)
               stats['status_code'] = response.status_code
               stats['url'] = url

               if self.debug:
                   print "[{2}] {1} :{0}".format(stats['url'], stats['duration'], datetime.datetime.now())

               try:
                   # calling this will throw an error for anything other than a
                   # successful response.
                   response.raise_for_status()
               except (MissingSchema, InvalidSchema, InvalidURL):
                   raise
               except RequestException as e:
                   events.request_failure.fire(
                       request_type = 'GET',
                       name = url,
                       response_time = stats['duration'],
                       exception = e
                   )
               else:
                   events.request_success.fire(
                       request_type = 'GET',
                       name = url,
                       response_time = stats['duration'],
                       response_length = stats['content_size']
                   )

                   if stats['duration'] > SLOW_REQUEST_THRESHOLD:
                       # TODO: record the request here.
                       events.request_slow.fire (
                           name = url,
                           response_time = stats['duration'],
                           response_length = stats['content_size']
                       )

           if self.debug and int((time.time() - start) * 1000) > 1000:
               print "[{0}] ****** slow request {1} :{2}".format(datetime.datetime.now(), stats['url'], stats['duration'])

           millis = random.randint(self.min_wait, self.max_wait)
           seconds = millis / 1000.0
           gevent.sleep(seconds)

    def start_workers(self, count):
        # put random sleep in here, so that all workers aren't started at exactly the
        # same time between clients. Should stop a peak/trough request cycle
        millis = random.randint(1, 1000)
        seconds = millis / 1000.0
        gevent.sleep(seconds)

        self.stop_workers(count)
        for i in range(count):
            self.workers.spawn(self.worker)
        self.worker_count += count;
        print "Started {} workers".format(count)
        return

    def stop_workers(self,count):
        self.workers.kill(block=True)
        self.worker_count = 0
        return


    def stats_reporter(self):
        while True:
            data = {'workers': self.worker_count}
            events.report_to_master.fire(client_id=self.slave_id, data=data)
            if self.debug:
                print data
            self.client.send(Message('client-stats', data, self.slave_id))
            gevent.sleep(STATS_REPORT_INTERVAL)

