import threading
from threading import Thread
import json
import time
import requests


class ReplicationService():

    def __init__(self, secondaries, retries, retry_delay):
        self.secondaries = secondaries
        self.retries = retries
        self.retry_delay = retry_delay

    def replicate(self, request, concern=None):
        count = CountDownLatch(concern)

        for server in self.secondaries:
            Thread(target=self.replicate_on, args=[request, server, count]).start()

        print(f"Wait for write with concern {concern}")
        count.await_zero()
        print(f"Finished write with concern {count.count}")
        print(f"Updated secondaries")


    def replicate_on(self, request, server, count):
        tries = self.retries

        while tries > 0:
            print(f"Send update for secondary server try {self.retries - tries + 1} on {server}")
            try:
                resp = requests.post(server, json.dumps(request))
                print(f"Received response from secondary {server} server {resp} {resp.content}")

                if resp.status_code == 200:
                    # зменшити лічильник якщо все ок
                    count.count_down()
                    break
                elif resp.status_code == 500:
                    # спробувати ще якщо помилка
                    tries -= 1
                    time.sleep(self.retry_delay)

            except requests.exceptions.ConnectionError:  # помилка зв'язку
                print(f"Connection error with secondary server {server}")
                tries -= 1
                time.sleep(self.retry_delay)


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