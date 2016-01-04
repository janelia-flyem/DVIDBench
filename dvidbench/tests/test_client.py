import unittest
from locust.rpc import rpc, Message

class ClientTestCase(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_communication(self):
        # start up a client
        client = rpc.Client('127.0.0.1', 8000)
        # send it a message
        print client
        # wait for response
        return

