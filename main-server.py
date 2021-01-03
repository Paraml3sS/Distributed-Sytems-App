import argparse
from request_handler import HandlersFactory
from server import run

if __name__ == '__main__':
    # Run master with configured secondary nodes as for e.g "-s http://localhost:5001/ -s http://localhost:5002/"
    parser = argparse.ArgumentParser(description='Starts master node')
    parser.add_argument('-s', '--secondaries', type=str, action='append', help='secondary servers addresses')
    parser.add_argument('-p', '--port', type=int, help='set receiving port', default=8000)
    parser.add_argument('-hd', '--heartbeat_delay', type=int, help='set heartbeat delay for secondary', default=10)
    parser.add_argument('-rd', '--retry_delay', type=int, help='set retry delay replicate to secondary', default=1)
    parser.add_argument('-ri', '--immediate_retry', type=bool, help='set first retry immediate', default=True)
    parser.add_argument('-rs', '--retry_strategy_name', type=str, help='retry strategy name: exponential, incremental, interval', default='interval')
    arguments = parser.parse_args()
    if arguments.secondaries:
        servers = arguments.secondaries

    run(ip_address="0.0.0.0", port=arguments.port, handler=HandlersFactory().get_main(arguments.secondaries, arguments))
