import argparse
from request_handler import HandlersFactory
from server import run

if __name__ == '__main__':
    # Run master with configured secondary nodes as for e.g "-s http://localhost:5001/ -s http://localhost:5002/"
    parser = argparse.ArgumentParser(description='Starts master node')
    parser.add_argument('-s', '--secondaries', type=str, action='append', help='secondary servers addresses')
    parser.add_argument('-p', '--port', type=int, help='set receiving port', default=8000)
    parser.add_argument('-r', '--retries', type=int, help='set retry on cannot replicate to secondary', default=3)
    parser.add_argument('-rd', '--retry_delay', type=int, help='set retry delay replicate to secondary', default=1)
    args = parser.parse_args()
    if args.secondaries:
        servers = args.secondaries

    run(ip_address="0.0.0.0", port=args.port, handler=HandlersFactory().get_main(args.secondaries, args.retries, args.retry_delay))
