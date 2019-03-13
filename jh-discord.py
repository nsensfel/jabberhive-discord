import discord
import asyncio
import argparse
import socket
import threading
from threading import Lock
import sys
import time

################################################################################
## MAIN ########################################################################
################################################################################
parser = argparse.ArgumentParser(
    description = (
        "Discord Client for JabberHive"
    )
)

parser.add_argument(
    '-d',
    '--destination',
    type = str,
    help = 'UNIX socket this client connects to.',
)

parser.add_argument(
    '-t',
    '--token',
    type = str,
    help = 'Discord token.',
)

parser.add_argument(
    '-c',
    '--print-chat',
    dest='print_chat',
    help = 'Prints all messages',
    action="store_true",
)

args = parser.parse_args()
is_connected = False
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client = discord.Client()
server_mutex = Lock()

def get_jh_reply ():
    global server

    is_done = False
    result = ""
    jh_reply = b""

    matched = 0

    while not is_done:
        c = b"\0"
        jh_reply = b""

        while (c != b"\n"):
            c = server.recv(1)
            jh_reply += c

        if ((jh_reply == b"!P \n") or (jh_reply == b"!N \n")):
            is_done = True
        else:
            jh_reply = jh_reply.decode("UTF-8")

            if (jh_reply.startswith("!GR ")):
                result = jh_reply[4:]
                result = result[:-1]

    return result

@client.event
async def on_ready():
    global is_connected
    global server
    global args

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if (not is_connected):
        server.connect(args.destination)
        is_connected = True

@client.event
async def on_message(message):
    global server
    global args
    global server_mutex

    if (message.author.id == client.user.id):
        return

    has_lock = False
    try:
        msg = bytes(message.clean_content.replace('\n', ' '), "utf8", 'strict')

        server_mutex.acquire()
        has_lock = True
        server.sendall(b"?RLR " + msg + b"\n")

        result = get_jh_reply()
        server_mutex.release()
        has_lock = False

        if (args.print_chat):
            print(
                str(message.server)
                + "#"
                + str(message.channel.name)
                + " <"
                + str(message.author.name)
                + "> "
                + str(message.clean_content)
            )

            if (len(result) > 0):
                print("#" + str(message.channel.name) + " <- " + result)

        if (len(result) > 0):
            await client.send_message(message.channel, result)
    except Exception as exception:
        if (has_lock):
            server_mutex.release()
        print(exception)

def exit_if_disconnected ():
    while True:
        time.sleep(61)

        if ((not client.is_logged_in) or client.is_closed):
            print("Timed out.")
            server.close()
            sys.exit()

threading.Thread(target=exit_if_disconnected).start()
client.run(args.token)
