# chatster

`chatster` is a Python CLI app that implements a small subset of both the IRC and Minecraft protocols. When running chatster, a local IRC server is created, where you can connect to any Minecraft server's chat via your favorite IRC client.

## Installation

To install chatster, ensure you have `python3` and `python3-pip` on your system, then run:

```sh
python3 -m pip install git+https://github.com/Ewpratten/chatster.git
```

## Usage

Running `chatster` from the commandline with no arguments will start an IRC server on `localhost:5556` for Minecraft `1.16.1`. These options can be configured via commandline flags:

```
usage: chatster [-h] [-i INTERFACE] [-p PORT] [-v MCVERSION]

optional arguments:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
                        IP address to bind to
  -p PORT, --port PORT  Port to bind to
  -v MCVERSION, --mcversion MCVERSION
                        Minecraft version to run
```

### Connecting with an IRC client

chatster uses IRC authentication to log you in to Minecraft. This means you will have to set the following options in your IRC client:

```
NICKNAME = Mojang account email
USERNAME = Minecraft username
PASSWORD = Mojang account password
```

Once connected to the chatster server, you will be able to join any Minecraft server with the following join command:

```
/join #mc.example.com:25565
```

chatster will parse the join command for a domain name, and attempt to open a connection to it. If this fails, you will see an error message.


### IRC features

Your IRC client should periodically update its users list, and you will see Minecraft usernames mapped to IRC usernames. You can manually send `/ping :1` to chatster to update the player list.

Player join, leave, sleep, and death messages are all announced to the IRC channel as well.