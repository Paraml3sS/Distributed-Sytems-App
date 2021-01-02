from http.server import BaseHTTPRequestHandler
import json
from urllib import parse
from replication_service import ReplicationService


logs = []


class HandlersFactory(object):
    def get_main(self, secondaries, args):
        replicator = ReplicationService(secondaries, args)

        class LogsRequestHandler(BaseHTTPRequestHandler):

            def __init__(self, *args, **kwargs):
                self.replicator = replicator
                super(LogsRequestHandler, self).__init__(*args, **kwargs)

            def do_GET(self):
                self._set_response()
                self.wfile.write(json.dumps(logs).encode())

            def do_POST(self):
                response = self._get_response()
                concern = self.parse_concern()

                new_message = response["log"]

                logs.append(new_message)
                concern -= 1

                print(f"Append new message: {new_message}")
                self.replicator.replicate(response, concern)

                self._set_response()
                self.wfile.write(json.dumps(response).encode())

            def _get_response(self):
                length = int(self.headers['content-length'])
                response = json.loads(self.rfile.read(length))
                print(f"Received POST request {response}")
                return response

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


        return LogsRequestHandler


