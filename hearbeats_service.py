import time
import requests
from http import HTTPStatus
from threading import Thread


class HeartbeatsService:

    def __init__(self, secondaries, heartbeat_delay=60):
        self.secondaries = secondaries
        self.heartbeat_delay = heartbeat_delay
        self.heartbeat_request_timeout = heartbeat_delay/3
        self.secondaries_status = dict()
        self.init_heartbeats()

    def init_heartbeats(self):
        for server in self.secondaries:
            Thread(target=self.heartbeat, args=[server]).start()
            self.secondaries_status[server] = 'Unknown'

    def get_heartbeats(self):
        return self.secondaries_status

    def heartbeat(self, server):
        while True:
            self.heartbeat_tick(server)
            time.sleep(self.heartbeat_delay)

    def heartbeat_tick(self, server):
        prev_status = self.secondaries_status.get(server, 'Unknown')
        try:
            resp = requests.get(server, timeout=self.heartbeat_request_timeout)

            if resp.status_code == HTTPStatus.OK:
                current_status = 'Healthy'
            else:
                current_status = 'Suspected'

        except requests.exceptions.ConnectionError:
            current_status = 'Suspected'

        if prev_status == 'Suspected' and current_status == 'Suspected':
            current_status = 'Unhealthy'

        self.secondaries_status[server] = current_status
