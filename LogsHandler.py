from http.server import BaseHTTPRequestHandler
import json

import requests

logs = []


class HandlersFactory(object):
    def get_main(self, secondaries):
        class LogsHandler(BaseHTTPRequestHandler):

            def do_GET(self):
                self._set_response()
                self.wfile.write(json.dumps(logs).encode())

            def do_POST(self):
                length = int(self.headers['content-length'])
                response = json.loads(self.rfile.read(length))
                print(f"Received POST request {response}")
                new_message = response["log"]
                logs.append(new_message)
                print(f"Append new message: {new_message}")

                for server in secondaries:
                    print(f"Send update for secondary server on {server}")
                    resp = requests.post(server, json.dumps(response))
                    print(f"Received response from secondary server {resp.content}")

                print(f"Updated secondaries")

                self._set_response()
                self.wfile.write(json.dumps(response).encode())

            def _set_response(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

        return LogsHandler
