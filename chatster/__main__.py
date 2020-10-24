import socketserver
import argparse
from threading import Thread
from typing import *
from minecraft.networking.packets.clientbound.play import ChatMessagePacket
from minecraft.networking.connection import Connection
from minecraft.authentication import AuthenticationToken
from minecraft.exceptions import YggdrasilError
from minecraft.networking.packets import serverbound
from minecraft import SUPPORTED_MINECRAFT_VERSIONS

# Consts
SERVER_NAME = "Chatster"
MOTD = "Use '/join mc.example.com' to join a server"

# IRC codes
RPL_WELCOME = '001'
ERR_NOSUCHNICK = '401'
ERR_NOSUCHCHANNEL = '403'
ERR_CANNOTSENDTOCHAN = '404'
ERR_UNKNOWNCOMMAND = '421'
ERR_ERRONEUSNICKNAME = '432'
ERR_NICKNAMEINUSE = '433'
ERR_NEEDMOREPARAMS = '461'

GLOBL_MC_VERSION = SUPPORTED_MINECRAFT_VERSIONS["1.16.1"]

def handleNick(self, data):

    # set email
    self.email = data[0][1:]
    print(f"{self.email} joined")

    # Ack
    return ":{server} {status} {nick} :{motd}".format(
        server=SERVER_NAME, status=RPL_WELCOME, nick=self.email, motd=MOTD).encode()


def handleUser(self, data):

    # Set username
    self.username = data[0]
    print(f"{self.email} is {self.username}")

    return (b"")


def handleID(self, data):

    # Set username
    self.password = data[0]
    print(f"{self.email} set password")

    return (b"Done")


def pingPong(self, _):

    return (":{server} PONG :{server}".format(
        server=SERVER_NAME).encode())


def buildPlayerList(self):

    return '\r\n'.join([
        ":{server} 353 {nick} = {channel} :{nicks}".format(
            SERVER_NAME, self.username, self.channel, " ".join(self.online_players)),
        ":{server} 366 {nick} {channel} :End of /NAMES list".format(
            SERVER_NAME, self.username, self.channel)
    ])


def handleJoin(self, data):

    # Get server
    server = data[0].split(':')
    port = 25565
    if len(server) == 2:
        port = int(server[1])

    server = server[0]
    self.channel = server

    status = self.connectToMC(server, port)

    if status:
        return status

    output = []

    output.append(f":{self.username} JOIN :{self.channel}\r\n")
    output.append(buildPlayerList(self))

    return "".join(output).encode()


class IRCHandler(socketserver.BaseRequestHandler):

    # MC player data
    username: str = None
    email: str = None
    password: str = None
    auth: AuthenticationToken = None
    connection: Connection = None

    online_players = ["server"]

    channel = "none"

    # IRC command handling
    command_handlers = {
        "NICK": handleNick,
        "USER": handleUser,
        "PASS": handleID,
        "PING": pingPong,
        "JOIN": handleJoin
    }

    def __init__(_, selfrequest, client_address, self):
        super().__init__(selfrequest, client_address, self)

    def handleIncomingChat(self, packet):
        print(packet)

    def sendChat(self, message):
        if self.connection:
            packet = serverbound.play.ChatPacket()
            packet.message = message
            self.connection.write_packet(packet)

    def connectToMC(self, server: str, port: int):

        if not (self.username or self.email or self.password):
            return b"Missing login info"

        try:
            # Build auth
            self.auth = AuthenticationToken()
            self.auth.authenticate(self.email, self.password)

            # Connect

            self.connection = Connection(server, port, self.auth, allowed_versions=[GLOBL_MC_VERSION])
            self.connection.connect()
        except YggdrasilError as e:
            return str(e.yggdrasil_message).encode()

        def chatWrapper(packet):
            self.handleIncomingChat()

        # Set up chat handler
        self.connection.register_packet_listener(chatWrapper, ChatMessagePacket)
        return None

    def handle(self):
        while True:

            # Read the incoming data
            self.data: bytes = self.request.recv(1024).strip()

            # Handle disconnect
            if not self.data:
                continue

            # Try to come up with a way to handle the message
            split_dat: List[str] = self.data.decode().split(" ")
            if len(split_dat) >= 1 and split_dat[0].upper() in self.command_handlers:
                message = self.command_handlers[split_dat[0].upper()](
                    self, split_dat[1:])

                if message:
                    self.request.send(message + b'\r\n')
            else:
                print("Unknown command: {cmd}".format(cmd=" ".join(split_dat)))

    def finish(self):

        # if self.auth:
        #     self.auth.sign_out(self.username, self.password)

        if self.connection:
            self.connection.disconnect()

        print(f"{self.username} left")


if __name__ == "__main__":

    # Parse any settings
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--interface",
                    help="IP address to bind to", default="localhost")
    ap.add_argument("-p", "--port", help="Port to bind to",
                    default="5556", type=int)
    ap.add_argument("-v", "--mcversion", help="Minecraft version to run",
                    default="1.16.1")
    args = ap.parse_args()

    if args.mcversion in SUPPORTED_MINECRAFT_VERSIONS:
        GLOBL_MC_VERSION = SUPPORTED_MINECRAFT_VERSIONS[args.mcversion]

    # Start up the server
    server = socketserver.TCPServer((args.interface, args.port), IRCHandler)
    server.serve_forever()
