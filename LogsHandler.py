from http.server import BaseHTTPRequestHandler
import json

logs = ["existing log"]


class LogsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self._set_response()
        self.wfile.write(json.dumps(logs).encode())

    def do_POST(self):
        length = int(self.headers['content-length'])
        response = json.loads(self.rfile.read(length))

        logs.append(response["log"])

        self._set_response()
        self.wfile.write(json.dumps(response).encode())

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
