import os
from typing import Dict, Tuple

import discord
from discord.channel import TextChannel
from discord.ext import tasks
from discord.guild import Guild
from discord.message import Message
from dotenv import load_dotenv

from utils import (STATE_PATH, get_server_status, is_admin, load_master_list,
                   log, save_master_list)

# Setup
load_dotenv()
client = discord.Client()

# Entries are int keys and tuple values with the following structure:
# guild_id: (admin_id, channel_id, message_id, server_hostname, server_up)
master_list: Dict[int, Tuple[int, int, int, str, bool]] = {}


async def parse_command(message: Message):
    command = message.content.split()
    log("parse_command - Received command {}".format(command))

    if len(command) < 2 and command[0] != "/mmm":
        return

    if command[1] == "status" and len(command) == 3:
        log("parse_command - Received 'status' command for guild ", message.guild)

        log("parse_command - Deleting messages on channel {}".format(message.channel.name))
        deleted = await message.channel.purge()
        log("parse_command - Deleted {} message(s) on the channel".format(len(deleted)))

        log("parse_command - Creating server status message")
        status_message = await message.channel.send(content="This message will contain the server info!")

        master_list[status_message.guild.id] = (
            message.author.id, status_message.channel.id, status_message.id, command[2], True)

        save_master_list(master_list, STATE_PATH)
    elif command[1] == "stop":
        log("parse_command - Stopping updates for guild ", message.guild.name)

        if message.guild.id in master_list:
            del master_list[message.guild.id]
            await message.channel.send(content="Sounds good! I'll stop updating this server")
            save_master_list(master_list, STATE_PATH)
        else:
            await message.channel.send(content="I'm not currently sending updates to this server")


@tasks.loop(minutes=1)
async def update_status():
    global master_list
    log("update_status - Processing master_list entries")

    for guild_id, (admin_id, channel_id, message_id, server_hostname, server_up) in master_list.items():
        guild: Guild = client.get_guild(guild_id)
        channel: TextChannel = guild.get_channel(channel_id)
        status_message = await channel.fetch_message(message_id)

        log("update_status - Fetching server status for guild", guild.name)
        status, new_server_up = await get_server_status(server_hostname)
        log("update_status - Fetch completed successfully")

        # Server recently down
        if server_up and not new_server_up:
            log("update_status - Server is just now down, sending DM to admin")
            admin = await client.fetch_user(admin_id)
            await admin.send(content="The server {} is down. Your guild {} has been updated.".format(server_hostname, guild.name))

        master_list[guild_id] = (admin_id, channel_id,
                                 message_id, server_hostname, new_server_up)

        log("update_status - Editing message in channel", channel.name)
        await status_message.edit(content=status)
        log("update_status - Message edited successfully")

    log("update_status - Saving master_list")
    save_master_list(master_list, STATE_PATH)


@client.event
async def on_message(message: Message):
    if message.author == client.user or not is_admin(message.author):
        return

    await parse_command(message)


@client.event
async def on_ready():
    global master_list
    log("on_ready - Logged in as {}".format(client.user))

    master_list = load_master_list(STATE_PATH)

    log("on_ready - Loaded master list with {} entrie(s)".format(len(master_list)))

    update_status.start()

client.run(os.getenv("TOKEN"))
