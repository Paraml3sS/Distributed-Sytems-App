import argparse
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler


class Secondary(BaseHTTPRequestHandler):

    log_messages = []

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'log_messages': self.log_messages
        }).encode())
        return

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
        self.log_messages.append(new_message)
        print(f"Append new message: {new_message}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'request_data': data,
            'new_message': new_message,
            'log_messages': self.log_messages
        }).encode())
        return


def run(ip_address, port):
    httpd = HTTPServer((ip_address, port), Secondary)
    print(f'Staring secondary on http://{ip_address}:{port}')
    httpd.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip_address", help="secondary ip adress", default='0.0.0.0', type=str)
    parser.add_argument("--port", help="secondary port", default=8000, type=int)
    args = parser.parse_args()
    run(ip_address=args.ip_address, port=int(args.port))
