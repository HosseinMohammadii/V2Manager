from datetime import datetime

from utils.size import convert_byte_to_gigabyte
from utils.marzban import get_marzban_token


marzban_token = {}


def get_marzban_cached_token(server):
    t = marzban_token.get(server.panel_add, None)
    if t is None:
        t = get_marzban_token(server.panel_add, server.username, server.password)
        marzban_token[server.panel_add] = t
    return t


def check_and_disable_subs(qs):
    disabled_subs = []
    for sub in qs:
        if datetime.today() > sub.expire_date:
            sub.disable()
            sub.update_status_dis_time()
            disabled_subs.append(sub)
            continue

        tr = sub.get_traffic()
        if convert_byte_to_gigabyte(tr) > sub.traffic:
            sub.disable()
            sub.update_status_dis_traffic()
            disabled_subs.append(sub)

    return disabled_subs


