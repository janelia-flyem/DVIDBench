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
from config import Configurable

STATS_REPORT_INTERVAL = 3
SLOW_REQUEST_THRESHOLD = 1000 #ms

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

runner = None

class Manager(Configurable):

    def __init__(self, options):
        self.manager_id = socket.gethostname() + "_" + str(uuid.uuid1())
        self.master_host = options.master_host
        self.master_port = options.master_port
        self.client = rpc.Client(self.master_host, self.master_port)
        self.config = self.load_config_data(options)
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
        return self.manager_id

    def listener(self):
        while True:
            msg = self.client.recv()
            if msg.type == 'quit':
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
        self.stop_workers(0)
        # message back to master?
        self.client.send(Message('client-quit', "i'm a gonner", self.identity))
        # exit
        exit(0)

    def worker(self):
       while True:
           url = self.config.url()


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
                       events.request_slow.fire (
                           name = url,
                           response_time = stats['duration'],
                           response_length = stats['content_size']
                       )

           if self.debug and int((time.time() - start) * 1000) > SLOW_REQUEST_THRESHOLD:
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
        print "stopped all workers"
        return


    def stats_reporter(self):
        while True:
            data = {'workers': self.worker_count}
            events.report_to_master.fire(client_id=self.manager_id, data=data)
            if self.debug:
                print data
            self.client.send(Message('client-stats', data, self.manager_id))
            gevent.sleep(STATS_REPORT_INTERVAL)

