import re

import urllib3
from threading import Thread
from unittest import TestCase, TextTestRunner, defaultTestLoader
from server import Server


class CheckServer(TestCase):

    def setUp(self):
        self.server = Server("127.0.0.1", 9999)
        self.thread_server = Thread(target=self.server.start)
        self.thread_server.start()

    def tearDown(self):
        if self.server:
            self.server.stop()
            self.thread_server.join()

    def test_contains_tm(self):
        http = urllib3.PoolManager()
        response = http.request("GET", "http://127.0.0.1:9999/ru/post/208680/")
        encoding = re.findall(r"charset=(.+)", response.headers["Content-Type"])[0]
        text = response.data.decode(encoding)
        six_words = re.findall(r"([\w]{6}™)", text)
        self.assertTrue(len(six_words) > 100, "Not find (tm)™")


if __name__ == "__main__":
    tests = defaultTestLoader.loadTestsFromTestCase(CheckServer)
    result = TextTestRunner().run(tests)
