import os

import discord
from dotenv import load_dotenv

from utils import (STATE_PATH, get_server_status, load_master_list, log,
                   save_master_list)

# Setup
load_dotenv()
client = discord.Client()


@client.event
async def on_ready():
    log("on_ready - Logged in as {}".format(client.user))

    master_list = load_master_list(STATE_PATH)

    for guild_id, (admin_id, channel_id, message_id, server_hostname, server_up) in master_list.items():
        print(guild_id, admin_id, channel_id,
              message_id, server_hostname, server_up)

        guild = client.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        status_message = await channel.fetch_message(message_id)

        log("on_ready - Getting server status for guild", guild.name)
        status, new_server_up = await get_server_status(server_hostname)

        # Server now down
        if server_up and not new_server_up:
            admin = await client.fetch_user(admin_id)
            await admin.send(content="The server is down D:")

        master_list[guild_id] = (admin_id, channel_id,
                                 message_id, server_hostname, new_server_up)

        log("on_ready - Editing Message in channel", channel.name)
        await status_message.edit(content=status)
        log("on_ready - Message edited successfully")

    save_master_list(master_list, STATE_PATH)
    await client.close()

client.run(os.getenv("TOKEN"))
