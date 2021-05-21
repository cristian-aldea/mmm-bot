import os
import pickle
from datetime import datetime
from typing import Dict, Tuple

from mcstatus import MinecraftServer

LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
UPDATE_TIMESTAMP_FORMAT = "%b %d %Y, %H:%M:%S UTC"

dirname = os.path.dirname(__file__)
STATE_PATH = os.path.join(dirname, "state/master.pkl")


def now_time(dt_format) -> str:
    now = datetime.utcnow()
    return now.strftime(dt_format)


def is_admin(user) -> bool:
    return user.guild_permissions.administrator


def log(*args) -> None:
    print(now_time(LOG_TIMESTAMP_FORMAT), "-", *args)


def save_master_list(obj, path) -> None:
    with open(path, "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_master_list(path) -> Dict[int, Tuple]:
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except:
        print(path, " not present")
        return {}


async def get_server_status(server_host) -> Tuple[str, bool]:
    server = MinecraftServer.lookup(server_host)
    try:
        status = server.status()
        message_text = ":white_check_mark:  `{}` is online!\n\n{}/{} player are playing!\n\nLast updated on {}"\
            .format(server_host,
                    status.players.online,
                    status.players.max,
                    now_time(UPDATE_TIMESTAMP_FORMAT))
        server_up = True
    except:
        message_text = ":warning:  `{}` isn't responding. The admin has been notified and should solve the issue soon :)\n\nLast updated on {}"\
            .format(server_host, now_time(UPDATE_TIMESTAMP_FORMAT))
        server_up = False
    return message_text, server_up
