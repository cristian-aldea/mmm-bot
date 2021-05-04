from datetime import datetime

import discord
from mcstatus import MinecraftServer

LOG_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
UPDATE_TIMESTAMP_FORMAT = '%b %d %Y, %H:%M:%S UTC'


def now_time(dt_format) -> str:
    now = datetime.now()
    return now.strftime(dt_format)


def is_user_admin(user) -> bool:
    admin_role = discord.utils.get(user.roles, name='Admin')
    return not admin_role == None


def get_server_status(channel, server_url) -> str:
    server = MinecraftServer.lookup(server_url)
    try:
        status = server.status()
        message_text = ':white_check_mark: `{}` is online!\n\n{}/{} player are playing!\n\nLast updated on {}'\
            .format(server_url,
                    status.players.online,
                    status.players.max,
                    now_time(UPDATE_TIMESTAMP_FORMAT))
    except:
        message_text = ':warning: `{}` isn\'t responding\n\nLast updated on {}'\
            .format(server_url, now_time(UPDATE_TIMESTAMP_FORMAT))

    return message_text


def log(message):
    print(now_time(LOG_TIMESTAMP_FORMAT), "-", message)
