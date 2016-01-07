import json
import time

class Stats(object):

    def __init__(self):
        pass

    # method to record stats for a response
    def add(self, data):
        print "saving: {}".format(data)
    # method to return summary stats
    # method to calculate stats for single url

class ClientStats(object):
    '''
    Collect aggregate stats for all the requests made by a client.
    '''
    workers = 0

    requests = []

    def __init__(self):
        pass

    def serialize(self):
        return {
            'workers': self.workers,
            'requests': self.requests
        }

    def unserialize(self):
        return

    def add(self, stats):
        stats['timestamp'] = time.time()
        self.requests.append(stats)
        return

    def clear(self):
        self.requests = []
        return
