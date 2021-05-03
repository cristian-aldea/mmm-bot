import os

import discord
from mcstatus import MinecraftServer

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$status') and message.channel.name == 'mmm-bot':
        deleted = await message.channel.purge()
        print('Deleted {} message(s) on the channel'.format(len(deleted)))

        server = MinecraftServer.lookup("mmm-server.com")

        try:
            status = server.status()
            message_text = ':white_check_mark: The server is online! {}/{} player are playing!'.format(
                status.players.online, status.players.max)
        except:
            message_text = ':warning: The server currently isn\'t responding.'
            await message.channel.send(message.author.mention)
        await message.channel.send(message_text)


client.run(os.getenv('TOKEN'))
