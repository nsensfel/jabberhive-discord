import discord
import asyncio
import argparse
import socket


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

args = parser.parse_args()
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

client = discord.Client()

def get_jh_reply ():
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

        print(jh_reply)

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
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    server.connect(args.destination)

@client.event
async def on_message(message):
    server.sendall(b"?RLR " + bytes(message.content, "utf8") + b"\n")
    result = get_jh_reply()
    print("Result: " + result)

    if (len(result) > 0):
        await client.send_message(message.channel, result)

client.run(args.token)
