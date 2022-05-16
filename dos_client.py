import argparse
import cmd
import pickle
import rsa
import socket
import threading

from criptography import BlowfishCriptography


class User(cmd.Cmd, threading.Thread):

    def __init__(self, connection):
        cmd.Cmd.__init__(self)
        threading.Thread.__init__(self)
        self.connection = connection
        self.reader = connection.makefile('rb', -1)
        self.writer = connection.makefile('wb', 0)

        (public_key, private_key) = rsa.newkeys(512)
        self.public_key = public_key
        self.private_key = private_key
    
    prompt = 'Insert here: '

    def start(self):
        super().start()
        #super().cmdloop() # commented line consequence: terminal doesnt block waiting for an input
        #self.cleanup() # commented line consequence: the thread created for a client no more finishes

    def cleanup(self):
        self.writer.flush()
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        self.join()

    def run(self):
        try:
            while True:
                self.handle_server_command()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def handle_server_command(self):

        source, obj = pickle.load(self.reader)
    
        if obj['code'] == '2':
            message = None
            try:
                message = self.cipher.decrypt(obj['content'])
            except UnicodeDecodeError:
                pass

            if message is None:
                message = obj['content']

            print(f'\n{source}: {message}')
        else:
            key = obj['content']
            key = rsa.decrypt(key, self.private_key)
            self.cipher = BlowfishCriptography(key)

            # Message: <client> just entered
            pickle.dump({'code': '2', 'content': self.cipher.encrypt(f'{(self.connection.getsockname())} just entered.')}, self.writer)

    def preloop(self):
        # Registering user
        pickle.dump({'code': '1', 'content': self.public_key}, self.writer)

    def do_say(self, arg):
        message = {'code': '2', 'content': self.cipher.encrypt(arg)}
        pickle.dump(message, self.writer)
        print(f'You: {arg}')

    def do_exit(self, arg):
        return True

    def postloop(self):
        message = {'code': '2', 'content': self.cipher.encrypt(f'{self.connection.getsockname()} just exited.')}
        pickle.dump(message, self.writer)


parser = argparse.ArgumentParser(description='Execute a chat client demo.')
parser.add_argument('host', type=str, help='name of server on the network')
parser.add_argument('port', type=int, help='location where server listens')
arguments = parser.parse_args()

count_client = 0

# server can keep up until around 1k clients at the same time
while count_client < 1200:
    client = User(socket.create_connection((arguments.host, arguments.port)))
    client.start()
    count_client += 1
    print(f" client {count_client} created")


