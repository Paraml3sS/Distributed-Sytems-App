import threading

def append(data, collection):
    current_counter = data.get('counter')

    if len(collection) <= current_counter:
        collection.extend([None] * (current_counter - len(collection) + 1))

    collection[current_counter - 1] = data.get('log')

    return data


class CountUpRequest(object):
    def __init__(self, count=0):
        self.count = count
        self.lock = threading.Condition()

    def count_up(self, request):
        with self.lock:
            self.count += 1
            request['counter'] = self.count
