from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib import parse
from replication_service import ReplicationService
import threading
import time

lock = threading.Condition()
logs = []
counter = 0


class HandlersFactory(object):
    def get_main(self, secondaries, arguments):
        replicator = ReplicationService(secondaries, arguments)

        class LogsRequestHandler(BaseHTTPRequestHandler):

            def __init__(self, *args, **kwargs):
                self.replicator = replicator
                self.secondaries = secondaries
                self.check_heartbeat = True
                self.heartbeat_timeout = 30
                t = threading.Thread(target=self.heartbeat)
                t.start()
                self.secondaries_status = 'Unknown'
                super(LogsRequestHandler, self).__init__(*args, **kwargs)

            def do_GET(self):
                self._set_response()
                if self.path == '/health':
                    print(f"Checking HEALTH status")
                    self.wfile.write(json.dumps(self.secondaries_status).encode())
                    return
                self.wfile.write(json.dumps(logs).encode())

            def do_POST(self):
                global counter
                request = self._parse_request()
                concern = self.parse_concern()

                new_message = request["log"]

                with lock:
                    counter += 1
                    request['counter'] = counter

                logs.append(new_message)
                concern -= 1

                print(f"Append new message: {new_message}")
                self.replicator.replicate(request, concern)

                self._set_response()
                self.wfile.write(json.dumps(request).encode())

            def _parse_request(self):
                length = int(self.headers['content-length'])
                request = json.loads(self.rfile.read(length))
                print(f"Received POST request {request}")
                return request

            def _set_response(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

            def parse_concern(self):
                concern = int(len(secondaries) / 2) + 1  # по замовчуванню записуємо в більшість

                query = parse.parse_qs(parse.urlsplit(self.path).query)
                if query.get('concern'):
                    concern = int(query.get('concern')[0])
                return concern

            def heartbeat(self):
                while self.check_heartbeat:
                    self.heartbeat_tick()
                    time.sleep(self.heartbeat_timeout)

            def heartbeat_tick(self):
                responses = []
                for s in self.secondaries:
                    resp = requests.get(s, timeout=3)
                    responses.append(resp.status_code)
                if list(set(responses)) == [200]:
                    print('Healthy')
                    self.secondaries_status = 'Healthy'
                elif 200 in responses:
                    print('Suspected')
                    self.secondaries_status = 'Suspected'
                else:
                    print('Unhealthy')
                    self.secondaries_status = 'Unhealthy'

        return LogsRequestHandler
