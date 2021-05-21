import os

import discord
from dotenv import load_dotenv

from utils import STATE_PATH, is_admin, load_master_list, log, save_master_list

# Setup
load_dotenv()
client = discord.Client()


# Entries are int keys and tuple values with the following structure:
# guild_id: (admin_id, channel_id, message_id, server_hostname, server_up)
master_list = {}


async def parse_command(message):
    command = message.content.split()
    log("parse_command - Received command {}".format(command))

    if command[0] == "/mmm" and command[1] == "status":
        log("parse_command - Deleting messages on channel {}".format(message.channel.name))
        deleted = await message.channel.purge()
        log("parse_command - Deleted {} message(s) on the channel".format(len(deleted)))

        log("parse_command - Creating server status message")
        status_message = await message.channel.send(content="This message will contain the server info!")

        master_list[status_message.guild.id] = (
            message.author.id, status_message.channel.id, status_message.id, command[2], True)

        save_master_list(master_list, STATE_PATH)
    elif command[0] == "/mmm" and command[1] == "stop":
        if message.guild.id in master_list:
            del master_list[message.guild.id]
            await message.channel.send(content="Sounds good! I'll stop updating this server")
            save_master_list(master_list, STATE_PATH)
        else:
            await message.channel.send(content="I'm not currently sending updates to this server")


@client.event
async def on_ready():
    global master_list
    log("on_ready - Logged in as {}".format(client.user))

    master_list = load_master_list(STATE_PATH)

    print("on_ready - Loaded master list:", master_list)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if is_admin(message.author):
        await parse_command(message)


client.run(os.getenv("TOKEN"))
