from client import *

HOST = '127.0.1.1'
PORT = 5050

count_client = 1

while (True):

    client = User(socket.create_connection((HOST, PORT)))
    #client.start()
    print(f'client {count_client} has connected')
    count_client += 1