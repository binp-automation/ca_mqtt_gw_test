import time


class Client:
    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.d = config["direction"]
        self.ready = False

    def drop(self):
        raise NotImplementedError

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
            self.clients[conn["mqtt"]] = client
        while any([not c.ready for c in self.clients.values()]):
            time.sleep(0.1)
        self.enter()

    def __exit__(self, *args):
        self.exit()
        for client in self.clients.values():
            client.drop()
        self.clients = {}