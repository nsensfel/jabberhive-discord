#!/usr/bin/env Python3
import discord
import asyncio
import argparse
import socket
import threading
import random
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
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client = discord.Client()
server_mutex = Lock()
already_disconnected = False

def get_jh_reply ():
    global server

    server_mutex
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
            jh_reply = jh_reply.decode("UTF-8", "ignore")

            if (jh_reply.startswith("!GR ")):
                result = jh_reply[4:]
                result = result[:-1]

    return result


@client.event
async def on_disconnect ():
    global already_disconnected

    if (not already_disconnected):
        print('Disconnecting from JH network from on_disconnect?!')
        time.sleep(10)
        server.close()
        sys.exit("l.94")

@client.event
async def on_connect ():
    global args
    global client
    global server

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    try:
        server.connect(args.destination)
    except Exception as exception:
        print('Could not connect to JH network: ' + str(exception))
        time.sleep(10)
        client.close()
        sys.exit("l.113")

@client.event
async def on_message(message):
    global server
    global args
    global server_mutex

    if (message.author.id == client.user.id):
        return

    has_lock = False
    try:
        msg_encoded = message.clean_content.encode('utf-8')
        msg = msg_encoded.replace(b'\n', b' ')

        server_mutex.acquire()
        has_lock = True

        server.sendall(
            b"!AI username: "
            + message.author.display_name.encode('utf-8')
            + b"\n"
        )
        server.sendall(b"?RLR " + msg + b"\n")
        result = get_jh_reply()

        server_mutex.release()
        has_lock = False

        if (args.print_chat):
            print(
                str(message.guild)
                + "#"
                + str(message.channel.name)
                + " <"
                + str(message.author.name)
                + "> "
                + str(msg_encoded)
            )

            if (len(result) > 0):
                print("#" + str(message.channel.name) + " <- " + str(result.encode('utf-8')))

        if (len(result) > 0):
            await message.channel.send(result)
    except Exception as exception:
        if (has_lock):
            server_mutex.release()
        print(exception)
        time.sleep(10)
        server.close()
        client.close()
        sys.exit("l.189")

client.run(args.token)
