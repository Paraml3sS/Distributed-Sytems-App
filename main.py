from http.server import HTTPServer
from LogsHandler import LogsHandler


def run(server_class=HTTPServer, handler_class=LogsHandler, addr="0.0.0.0", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run()