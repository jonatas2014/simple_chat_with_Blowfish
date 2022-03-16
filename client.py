import argparse
import select
import socket
import sys

from constants import DEFAULT_KEY, ENCONDING_FORMAT
from criptography import BlowfishCriptography


def show_message_when_receive(socket, cipher):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", type=str, required=True, dest="host")
    parser.add_argument("--port", type=int, required=True, dest="port")
    parser.add_argument("--key", type=str, dest="key")

    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        
        server_socket.connect((args.host, args.port))

        cipher = BlowfishCriptography(key=args.key if args.key is not None else DEFAULT_KEY)
        
        while True:
            read_sockets, _, _ = select.select([server_socket, sys.stdin], [], [])

            for socket in read_sockets:
                if socket == sys.stdin:
                    message = sys.stdin.readline().strip()
                    encrypted_message = cipher.encrypt(message)
                    server_socket.send(encrypted_message)
                else:
                    encrypted_message = socket.recv(2048)
                    message = cipher.decrypt(encrypted_message)
                    print(message)
