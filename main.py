import argparse
import os
import threading
import time

import discord
from dotenv import load_dotenv

from utils import get_server_status, is_user_admin, log, now_time

load_dotenv()
client = discord.Client()

parser = argparse.ArgumentParser(
    description='Discord bot which gives live updates on the status of your server!')
parser.add_argument("--server-url", default="mmm-server.com",
                    help="The Minecraft Server URL to ping")
parser.add_argument("--ping-interval", type=int, default=1,
                    help="How often the bot should ping the server")

args = parser.parse_args()

server_url = args.server_url
ping_interval = args.ping_interval


loop_thread: threading.Thread = None
loop_stop_flag = False

loop_thread


async def parse_command(message):
    if message.content == "$status":

        global loop_thread, loop_stop_flag

        if loop_thread and loop_thread.is_alive() and not loop_stop_flag:
            log("Existing alive thread found. Sending stop signal and waiting for thread to stop")
            loop_stop_flag = True
            loop_thread.join()

        log("Creating thread for status subroutine")
        loop_thread = threading.Thread(
            target=await server_status_update_loop(message.channel))
        loop_thread.start()


async def server_status_update_loop(status_channel):
    global loop_stop_flag, loop_thread

    log("Deleting messages on channel {}".format(status_channel.name))
    deleted = await status_channel.purge()
    log('Deleted {} message(s) on the channel'.format(len(deleted)))

    log('Creating server status message')
    status_message = await status_channel.send(content=get_server_status(status_channel, server_url))

    log('Running loop to edit message every {} seconds to update the status message'.format(
        ping_interval))
    while True:
        time.sleep(ping_interval)
        log("Editing message with current server status")
        await status_message.edit(content=get_server_status(status_channel, server_url))
        if loop_stop_flag:
            loop_stop_flag = False
            break


@client.event
async def on_ready():
    log('Logged in as {}'.format(client.user))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if is_user_admin(message.author):
        await parse_command(message)


client.run(os.getenv('TOKEN'))
