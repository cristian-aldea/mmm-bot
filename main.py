import argparse
import asyncio
import os
import threading
import time

import discord
from dotenv import load_dotenv
from mcstatus import MinecraftServer

from utils import UPDATE_TIMESTAMP_FORMAT, is_admin, log, now_time

# Parse args
parser = argparse.ArgumentParser(
    description="Discord bot which gives live updates on the status of your server!")
parser.add_argument("--server-url", default="mmm-server.com",
                    help="The Minecraft Server URL to ping")
parser.add_argument("--ping-host", default="mmm-server.com",
                    help="The Minecraft Server Host to ping")
parser.add_argument("--ping-interval", type=int, default=5,
                    help="How often the bot should ping the server")

args = parser.parse_args()
ping_host = args.ping_host
server_url = args.server_url
ping_interval = args.ping_interval

# Setup
load_dotenv()
client = discord.Client()

# Globals
loop_task: asyncio.Task = None
loop_stop_flag = False
server_down = False
admin_user = None


async def stop_task():
    global loop_task, loop_stop_flag
    log("Stopping current loop_task if running")
    if loop_task and not loop_task.done() and not loop_stop_flag:
        loop_stop_flag = True
        await loop_task


async def parse_command(message):
    global loop_task
    command = message.content.split()
    log("Received command {}".format(command))

    if command[0] == "/mmm" and command[1] == "status":
        await stop_task()

        log("Creating new loop_task")
        # Creating coroutine to run asynchronously
        loop_task = asyncio.create_task(
            status_update_loop(message.channel))
    elif command[0] == "/mmm" and command[1] == "stop":
        await stop_task()


async def get_server_status(channel) -> str:
    global server_down, admin_user, server_url, ping_host

    server = MinecraftServer.lookup(ping_host)
    try:
        status = server.status()
        message_text = ":white_check_mark:  `{}` is online!\n\n{}/{} player are playing!\n\nLast updated on {}"\
            .format(server_url,
                    status.players.online,
                    status.players.max,
                    now_time(UPDATE_TIMESTAMP_FORMAT))

        if server_down:
            server_down = False
    except:
        message_text = ":warning:  `{}` isn't responding. The admin has been notified and should solve the issue soon :)\n\nLast updated on {}"\
            .format(server_url, now_time(UPDATE_TIMESTAMP_FORMAT))

        if not server_down:
            log("Server unavailable. Sending DM to user {}".format(admin_user))

            await admin_user.send(content="The server is down D:")
            server_down = True

    return message_text


async def status_update_loop(status_channel):
    global loop_stop_flag
    log("status_update_loop - Deleting messages on channel {}".format(status_channel.name))
    deleted = await status_channel.purge()
    log("status_update_loop - Deleted {} message(s) on the channel".format(len(deleted)))

    log("status_update_loop - Creating server status message")
    status_message = await status_channel.send(content=await get_server_status(status_channel))

    log("status_update_loop - Editing message every {} seconds with current status".format(ping_interval))

    while True:
        time.sleep(ping_interval)

        log("status_update_loop - Getting server status")
        status = await get_server_status(status_channel)

        log("status_update_loop - Editing Message")
        await status_message.edit(content=status)
        log("status_update_loop - Message edited successfully")

        if loop_stop_flag:
            log("status_update_loop - Loop stop flag caught. Exiting loop")
            loop_stop_flag = False
            break


@client.event
async def on_ready():
    log("Logged in as {}".format(client.user))


@client.event
async def on_message(message):
    global admin_user
    if message.author == client.user:
        return

    if is_admin(message.author):
        # keeping track of server admin for sending DMs
        admin_user = message.author
        await parse_command(message)


client.run(os.getenv("TOKEN"))
