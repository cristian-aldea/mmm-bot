from datetime import datetime

import discord

LOG_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
UPDATE_TIMESTAMP_FORMAT = '%b %d %Y, %H:%M:%S UTC'


def now_time(dt_format) -> str:
    now = datetime.now()
    return now.strftime(dt_format)


def is_admin(user) -> bool:
    admin_role = discord.utils.get(user.roles, name='Admin')
    return not admin_role == None


def log(*args):
    print(now_time(LOG_TIMESTAMP_FORMAT), "-", *args)
