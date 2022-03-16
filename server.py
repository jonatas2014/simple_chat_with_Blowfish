import argparse
import socketserver


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.request.sendall(self.data.upper())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", type=str, required=True, dest="host")
    parser.add_argument("--port", type=int, required=True, dest="port")

    args = parser.parse_args()

    with socketserver.TCPServer((args.host, args.port), TCPHandler) as server:
        server.serve_forever()
