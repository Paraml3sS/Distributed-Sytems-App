import argparse
from http.server import HTTPServer
from LogsHandler import HandlersFactory


def run_server(handler_class, server_class=HTTPServer, addr="0.0.0.0", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")

    try:
        httpd.serve_forever()
    finally:
        httpd.shutdown()


if __name__ == '__main__':
    # Run master with configured secondary nodes as for e.g "-s http://localhost:5001/ -s http://localhost:5002/"
    parser = argparse.ArgumentParser(description='Starts master node')
    parser.add_argument('-s', '--secondaries', type=str, action='append', help='secondary servers addresses')
    parser.add_argument('-p', '--port', type=int, help='set receiving port', default=8000)
    args = parser.parse_args()
    if args.secondaries:
        servers = args.secondaries

    run_server(HandlersFactory().get_main(args.secondaries), port=args.port)
