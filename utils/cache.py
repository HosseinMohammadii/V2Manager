import time
from datetime import datetime

from utils.marzban import get_marzban_token

marzban_token = {}


def get_marzban_cached_token(server):
    token_and_update = marzban_token.get(server.panel_add, None)

    if token_and_update is None:
        t = get_marzban_token(server.panel_add, server.username, server.password)
        marzban_token[server.panel_add] = (t, int(time.time()))
        return t

    token = token_and_update[0]
    update_time = token_and_update[1]

    if (int(time.time()) - update_time) > 500:
        token = get_marzban_token(server.panel_add, server.username, server.password)
        marzban_token[server.panel_add] = (token, int(time.time()))

    return token
