import os
import time

import discord
from dotenv import load_dotenv
from mcstatus import MinecraftServer

load_dotenv()
client = discord.Client()

admin_id = 124307510546006016
update_delay = 10


def get_server_status(channel):
    server = MinecraftServer.lookup("mmm-server.com")
    try:
        status = server.status()
        message_text = ':white_check_mark: The server is online! {}/{} player are playing!'.format(
            status.players.online, status.players.max)
    except:
        message_text = ':warning: The server currently isn\'t responding.'

    return message_text


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    mmm_server = client.guilds[0]
    print('Using guild "{}"'.format(mmm_server.name))

    status_channel = discord.utils.get(mmm_server.channels, name='mmm-status')
    print('Fetched channel by name: {}'.format(status_channel.name))

    deleted = await status_channel.purge()
    print('Deleted {} message(s) on the channel'.format(len(deleted)))

    print('Creating message with server status')
    status_message = await status_channel.send(content=get_server_status(status_channel))

    print('Now the message will be edited every {} seconds to update the status message'.format(
        update_delay))
    while True:
        time.sleep(update_delay)
        await status_message.edit(content=get_server_status(status_channel))


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return


client.run(os.getenv('TOKEN'))
