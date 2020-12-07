import threading
import time
from threading import Thread
from urllib import parse
from http.server import BaseHTTPRequestHandler
import json

import requests

logs = []


class HandlersFactory(object):
    def get_main(self, secondaries, retries, retry_delay):
        class LogsHandler(BaseHTTPRequestHandler):

            def do_GET(self):
                self._set_response()
                self.wfile.write(json.dumps(logs).encode())

            def do_POST(self):
                length = int(self.headers['content-length'])
                response = json.loads(self.rfile.read(length))
                print(f"Received POST request {response}")

                concern = self.parse_concern()

                new_message = response["log"]
                logs.append(new_message)
                concern -= 1
                print(f"Append new message: {new_message}")

                self.replicate(response, secondaries, concern)

                print(f"Updated secondaries")

                self._set_response()
                self.wfile.write(json.dumps(response).encode())

            def _set_response(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

            def replicate(self, request, secondaries, concern):
                count = CountDownLatch(concern)
                for server in secondaries:
                    Thread(target=self.replicate_on, args=[request, server, count]).start()

                print(f"Wait for write with concern {concern}")
                count.await_zero()
                print(f"Finished write with concern {concern}")

            @staticmethod
            def replicate_on(request, server, count):
                tries = retries

                while tries > 0:
                    print(f"Send update for secondary server try {retries - tries + 1} on {server}")
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
                            time.sleep(retry_delay)

                    except requests.exceptions.ConnectionError: # помилка зв'язку
                        print(f"Connection error with secondary server {server}")
                        tries -= 1
                        time.sleep(retry_delay)

            def parse_concern(self):
                query = parse.parse_qs(parse.urlsplit(self.path).query)
                concern = int(len(secondaries)/2) + 1  # по замовчуванню записуємо в більшість
                if query.get('concern'):
                    concern = int(query.get('concern')[0])
                return concern

        return LogsHandler


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