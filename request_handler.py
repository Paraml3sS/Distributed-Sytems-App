from http.server import BaseHTTPRequestHandler
import json
from urllib import parse
from hearbeats_service import HeartbeatsService
from replication_service import ReplicationService
import threading

lock = threading.Condition()
logs = []
counter = 0


class HandlersFactory(object):
    def get_main(self, secondaries, arguments):
        heartbeat_service = HeartbeatsService(secondaries, heartbeat_delay=arguments.heartbeat_delay)
        replicator = ReplicationService(secondaries, heartbeat_service, arguments)

        class LogsRequestHandler(BaseHTTPRequestHandler):

            def __init__(self, *args, **kwargs):
                self.replicator = replicator
                self.heartbeats = heartbeat_service
                self.quorum = self.calc_quorum()
                super(LogsRequestHandler, self).__init__(*args, **kwargs)

            def do_GET(self):
                self._set_response()
                if self.path == '/health':
                    print(f"Checking HEALTH status")
                    secondary_heartbeats = heartbeat_service.get_heartbeats()
                    self.wfile.write(json.dumps(secondary_heartbeats).encode())
                    return
                self.wfile.write(json.dumps(logs).encode())

            def do_POST(self):
                global counter
                request = self._parse_request()
                concern = self.parse_concern()

                if self.check_quorum():
                    return

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
                concern = self.quorum  # по замовчуванню записуємо в більшість

                query = parse.parse_qs(parse.urlsplit(self.path).query)
                if query.get('concern'):
                    concern = int(query.get('concern')[0])
                return concern

            def calc_quorum(self):
                return int(len(secondaries) / 2) + 1

            def check_quorum(self):
                live_count = heartbeat_service.get_live_count() + 1
                if live_count < self.quorum:
                    error_message = f'No quorum, only {live_count} nodes alive'
                    print(error_message)
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': error_message,
                    }).encode())
                    return True

        return LogsRequestHandler
