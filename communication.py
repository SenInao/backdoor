import socket
import pickle

class ObjectCommunication:
    def __init__(self, client:socket.socket) -> None:
        self.client = client

    def send(self, data):
        pack = pickle.dumps(data)
        size = len(pack)
        package = (str(size) + "<SIZE>").encode() + pack

        self.client.sendall(package)

    def receive(self):
        data = self.client.recv(1024)
        data = data.split(b"<SIZE>")

        size = int(data[0])
        package = data[1]
        remaining_size = size - len(package)
        while remaining_size > 0:
            package += self.client.recv(1024)
            remaining_size = size-len(package)

        return pickle.loads(package)

class ByteCommunication:
    def __init__(self, client) -> None:
        self.client = client

    def send(self, data:bytes):
        size = len(data)
        package = (str(size) + "<SIZE>").encode() + data

        self.client.sendall(package)

    def receive(self) -> bytes:
        data = self.client.recv(1024)
        data = data.split(b"<SIZE>")

        size = int(data[0])
        package = data[1]
        remaining_size = size - len(package)

        while remaining_size > 0:
            package += self.client.recv(min(remaining_size, bufferSize))
            remaining_size  = size - len(package)

        return package
        
bufferSize = 16384
