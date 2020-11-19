import argparse
import json
import time
from http.server import BaseHTTPRequestHandler

from server import MultiServer

log_messages = []


class SecondaryPublic(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'log_messages': log_messages
        }).encode())
        return


class SecondaryInternal(BaseHTTPRequestHandler):

    def do_POST(self):
        content_len = int(self.headers.get('content-length'))
        post_body = self.rfile.read(content_len)
        print(f"Received POST request: {post_body}")
        data = json.loads(post_body)
        response_delay = data.get('response_delay', 1)
        time.sleep(response_delay)
        new_message = data.get('log')
        if not new_message:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({
                'request_data': data,
            }).encode())
            return
        log_messages.append(new_message)
        print(f"Append new message: {new_message}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'request_data': data,
            'new_message': new_message,
            'log_messages': log_messages
        }).encode())
        return


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
