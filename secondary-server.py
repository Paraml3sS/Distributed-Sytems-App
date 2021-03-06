import argparse
import json
import random
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler

from server import MultiServer
from happy_helper import append


log_messages = []


class SecondaryPublic(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'log_messages': log_messages[0:log_messages.index(None)]
        }).encode())
        return


class SecondaryInternal(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        print(f"Beat {datetime.now()}")
        return

    def do_POST(self):
        content_len = int(self.headers.get('content-length'))
        post_body = self.rfile.read(content_len)
        print(f"Received POST request: {post_body}")
        data = json.loads(post_body)

        if self.emulate_error('error before saving', data):
            return

        self.emulate_delay(data)
        append(data, log_messages)

        if self.emulate_error('error after saving', data):
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'request_data': data,
            'log_messages': log_messages
        }).encode())
        return



    def emulate_error(self, error_message, request_data):
        probability = request_data.get(error_message, 0.3)

        if random.random() < probability:
            print(error_message)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': error_message,
            }).encode())
            return True

    def emulate_delay(self, request_data):
        response_delay = request_data.get('response_delay', random.random() * 10)
        time.sleep(response_delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Starts secondary node')
    parser.add_argument("--ip_address", help="public ip address", default='0.0.0.0', type=str)
    parser.add_argument("--port", help="public port", default=8000, type=int)
    parser.add_argument("--internal_port", help="internal port", default=5000, type=int)
    args = parser.parse_args()

    multi_server = MultiServer()
    multi_server.add(ip_address=args.ip_address, port=args.port, handler=SecondaryPublic)
    multi_server.add(ip_address=args.ip_address, port=int(args.internal_port), handler=SecondaryInternal)
    multi_server.run()
