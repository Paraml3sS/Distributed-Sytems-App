import time
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from threading import Thread


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class MultiServer(object):
    _threads = []  # list of tuples, where 0 - thread, 1 - http server

    def add(self, ip_address, port, handler):
        httpd = ThreadedHTTPServer((ip_address, port), handler)
        self._threads.append((Thread(target=__run__, args=[httpd]), httpd))

    def run(self):  # starts servers and waits until interruption to shutdown
        for thread in self._threads:
            thread[0].start()

        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt as e:
            print(repr(e))

        for thread in self._threads:
            print(f"closing {thread[1].server_address}")
            thread[1].shutdown()
            print(f"closed {thread[1].server_address}")


def __run__(httpd):
    print(f'Starting {httpd.RequestHandlerClass} on {httpd.server_address}')
    httpd.serve_forever()


def run(ip_address, port, handler):
    __run__(ThreadedHTTPServer((ip_address, port), handler))
