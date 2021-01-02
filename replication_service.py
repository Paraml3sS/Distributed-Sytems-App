import json
import threading
from http import HTTPStatus
from threading import Thread

import requests

from delay import RetryFactory


class ReplicationService():

    def __init__(self, secondaries, args):
        self.retries_factory = RetryFactory(args)
        self.secondaries = secondaries
        self.message_counter = 0

    def replicate(self, request, concern=None):
        self.message_counter += 1
        count = CountDownLatch(concern)

        request["counter"] = self.message_counter

        for server in self.secondaries:
            Thread(target=self.replicate_on, args=[request, server, count]).start()

        print(f"Wait for write with concern {concern}")
        count.await_zero()
        print(f"Finished write with concern {count.count}")
        print(f"Updated secondaries")


    def replicate_on(self, request, server, count):
        tries = 0
        retry_delayer = self.retries_factory.build()

        while True:
            print(f"Send update for secondary server try {tries + 1} on {server}")
            try:
                resp = requests.post(server, json.dumps(request))
                print(f"Received response from secondary {server} server {resp} {resp.content}")

                if resp.status_code == HTTPStatus.OK:
                    # зменшити лічильник якщо все ок
                    count.count_down()
                    break
                elif resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                    # спробувати ще якщо помилка
                    tries += 1
                    retry_delayer.delay()

            except requests.exceptions.ConnectionError:  # помилка зв'язку
                print(f"Connection error with secondary server {server}")
                tries += 1
                retry_delayer.delay()


class CountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            self.lock.notifyAll()
        self.lock.release()

    def await_zero(self):
        self.lock.acquire()
        self.lock.wait_for(lambda: self.count <= 0)
        self.lock.release()