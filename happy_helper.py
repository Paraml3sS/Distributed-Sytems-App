import threading

def append(data, collection):
    current_counter = data.get('counter')

    if len(collection) <= current_counter:
        collection.extend([None] * (current_counter - len(collection) + 1))

    collection[current_counter - 1] = data.get('log')

    return data

