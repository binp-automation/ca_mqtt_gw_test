import time
from queue import Queue, Empty

delay = 0.01 # s

class Client:
    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.d = config["direction"]
        self.ready = False
        self.rq = Queue()

    def drop(self):
        raise NotImplementedError

    def send(self, data):
        raise NotImplementedError

    def queue_recv(self, data):
        self.rq.put(data)

    def receive(self, timeout=None):
        try:
            return self.rq.get(timeout=timeout)
        except Empty:
            raise TimeoutError

    def clear(self):
        while not self.rq.empty():
            self.rq.get_nowait()

class Manager:
    def __init__(self, config):
        self.clients = {}
        self.config = config

    def __getitem__(self, key):
        return self.clients[key]

    def enter(self):
        raise NotImplementedError

    def exit(self, *args):
        raise NotImplementedError

    def create_client(self, config):
        raise NotImplementedError

    def __enter__(self):
        for conn in self.config["connections"]:
            client = self.create_client(conn)
            self.clients[client.name] = client
        while any([not c.ready for c in self.clients.values()]):
            time.sleep(delay)
        self.enter()

    def __exit__(self, *args):
        self.exit()
        for client in self.clients.values():
            client.drop()
        self.clients = {}