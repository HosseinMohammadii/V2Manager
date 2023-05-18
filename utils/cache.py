import time
from datetime import datetime

from utils.marzban import get_marzban_token

marzban_token = {}


def get_marzban_cached_token(server):
    t, update_time = marzban_token.get(server.panel_add, None)
    if t is None or (int(time.time()) - update_time) > 500:
        t = get_marzban_token(server.panel_add, server.username, server.password)
        marzban_token[server.panel_add] = (t, int(time.time()))
    return t
