import argparse
import pickle
import queue
import random
import rsa
import select
import socket
import socketserver


class CustomServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, request_handler_class):
        """Initialize the server and keep a set of registered clients."""
        super().__init__(server_address, request_handler_class, True)
        self.clients = set()
        self.key = self.__generate_random_key()

    def __generate_random_key(self):
        hash_ = random.getrandbits(128)
        hash_ = '%032x' % hash_
        return hash_

    def add_client(self, client):
        self.clients.add(client)

    def broadcast(self, source, data):
        for client in tuple(self.clients):
            if client is not source:
                client.schedule((source.name, data))

    def remove_client(self, client):
        self.clients.remove(client)


class CustomHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, client_address, server):
        self.buffer = queue.Queue()
        super().__init__(request, client_address, server)

    def setup(self):
        super().setup()
        self.server.add_client(self)

    def handle(self):
        try:
            while True:
                self.empty_buffers()
        except (ConnectionResetError, EOFError):
            pass

    def empty_buffers(self):
        if self.readable:
            data = pickle.load(self.rfile)
            if data['code'] == '1':
                public_key = data['content']
                data['content'] = rsa.encrypt(self.server.key.encode('utf-8'), public_key)
                self.schedule((self.name, data))
            else:
                self.server.broadcast(self, data)
        while not self.buffer.empty():
            pickle.dump(self.buffer.get_nowait(), self.wfile)

    @property
    def readable(self):
        return self.connection in select.select(
            (self.connection,), (), (), 0.1)[0]

    @property
    def name(self):
        return self.connection.getpeername()

    def schedule(self, data):
        self.buffer.put_nowait(data)

    def finish(self):
        self.server.remove_client(self)
        super().finish()


parser = argparse.ArgumentParser(description='Execute a chat server demo.')
parser.add_argument('port', type=int, help='location where server listens')
arguments = parser.parse_args()
server_address = socket.gethostbyname(socket.gethostname()), arguments.port
print(server_address)
server = CustomServer(server_address, CustomHandler)
server.serve_forever()
