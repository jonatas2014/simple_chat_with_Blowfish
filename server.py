import argparse
import pickle
import queue
import select
import socket
import socketserver


class CustomServer(socketserver.ThreadingTCPServer):

    """Provide server support for the management of connected clients."""

    def __init__(self, server_address, request_handler_class):
        """Initialize the server and keep a set of registered clients."""
        super().__init__(server_address, request_handler_class, True)
        self.clients = set()

    def add_client(self, client):
        """Register a client with the internal store of clients."""
        self.clients.add(client)

    def broadcast(self, source, data):
        """Resend data to all clients except for the data's source."""
        for client in tuple(self.clients):
            if client is not source:
                client.schedule((source.name, data))

    def remove_client(self, client):
        """Take a client off the register to disable broadcasts to it."""
        self.clients.remove(client)


class CustomHandler(socketserver.StreamRequestHandler):

    """Allow forwarding of data to all other registered clients."""

    def __init__(self, request, client_address, server):
        """Initialize the handler with a store for future date streams."""
        self.buffer = queue.Queue()
        super().__init__(request, client_address, server)

    def setup(self):
        """Register self with the clients the server has available."""
        super().setup()
        self.server.add_client(self)

    def handle(self):
        """Run a continuous message pump to broadcast all client data."""
        try:
            while True:
                self.empty_buffers()
        except (ConnectionResetError, EOFError):
            pass

    def empty_buffers(self):
        """Transfer data to other clients and write out all waiting data."""
        if self.readable:
            self.server.broadcast(self, pickle.load(self.rfile))
        while not self.buffer.empty():
            pickle.dump(self.buffer.get_nowait(), self.wfile)

    @property
    def readable(self):
        """Check if the client's connection can be read without blocking."""
        return self.connection in select.select(
            (self.connection,), (), (), 0.1)[0]

    @property
    def name(self):
        """Get the client's address to which the server is connected."""
        return self.connection.getpeername()

    def schedule(self, data):
        """Arrange for a data packet to be transmitted to the client."""
        self.buffer.put_nowait(data)

    def finish(self):
        """Remove the client's registration from the server before closing."""
        self.server.remove_client(self)
        super().finish()


parser = argparse.ArgumentParser(description='Execute a chat server demo.')
parser.add_argument('port', type=int, help='location where server listens')
arguments = parser.parse_args()
server_address = socket.gethostbyname(socket.gethostname()), arguments.port
print(server_address)
server = CustomServer(server_address, CustomHandler)
server.serve_forever()
