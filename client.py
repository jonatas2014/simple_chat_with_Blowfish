import argparse
import cmd
import pickle
import socket
import threading

from constants import DEFAULT_KEY
from criptography import BlowfishCriptography


class User(cmd.Cmd, threading.Thread):
    prompt = 'Insert here: '

    def __init__(self, connection, cipher):
        cmd.Cmd.__init__(self)
        threading.Thread.__init__(self)
        self.connection = connection
        self.cipher = cipher
        self.reader = connection.makefile('rb', -1)
        self.writer = connection.makefile('wb', 0)

    def start(self):
        """Begin execution of processor thread and user command loop."""
        super().start()
        super().cmdloop()
        self.cleanup()

    def cleanup(self):
        """Close the connection and wait for the thread to terminate."""
        self.writer.flush()
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        self.join()

    def run(self):
        """Execute an automated message pump for client communications."""
        try:
            while True:
                self.handle_server_command()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def handle_server_command(self):
        """Get an instruction from the server and execute it."""
        source, encrypted_message = pickle.load(self.reader)

        message = None
        try:
            message = self.cipher.decrypt(encrypted_message)
        except UnicodeDecodeError:
            pass

        if message is None:
            message = encrypted_message

        print(f'\n{source[0]}: {message}')

    def preloop(self):
        """Announce to other clients that we are connecting."""
        message = f'{socket.gethostname()} just entered.'
        message = self.cipher.encrypt(message)
        pickle.dump(message, self.writer)

    def do_say(self, arg):
        """Causes a message to appear to all other clients."""
        message = self.cipher.encrypt(arg)
        pickle.dump(message, self.writer)
        print(f'You: {arg}')

    def do_exit(self, arg):
        """Disconnect from the server and close the client."""
        return True

    def postloop(self):
        """Make an announcement to other clients that we are leaving."""
        message = f'{socket.gethostname()} just exited.'
        message = self.cipher.encrypt(message)
        pickle.dump(message, self.writer)


parser = argparse.ArgumentParser(description='Execute a chat client demo.')
parser.add_argument('host', type=str, help='name of server on the network')
parser.add_argument('port', type=int, help='location where server listens')
parser.add_argument('key', type=str)
arguments = parser.parse_args()
cipher = BlowfishCriptography(key=arguments.key if arguments.key is not None else DEFAULT_KEY)
client = User(socket.create_connection((arguments.host, arguments.port)), cipher)
client.start()
