from urllib import parse
from urllib.parse import urlencode

import requests


def get_xui_traffic(add, auth, id, ):
    url = f"{add}/xui/inbound/list"
    session = f"session={auth}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": session
    }
    try:
        res = requests.post(url, headers=headers)
        resj = res.json()
        for o in resj["obj"]:
            if o["id"] != int(id):
                continue
            return o["up"] + o["down"]
        return 0
    except requests.exceptions.RequestException:
        print("Couldn't get data from", add)

        return 0


def disable_enable_xui_config(add, auth, id, action: str):
    url = f"{add}/xui/inbound/list"
    session = f"session={auth}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": session
    }
    conf = None
    try:
        res = requests.post(url, headers=headers)
        resj = res.json()
        for o in resj["obj"]:
            if o["id"] == int(id):
                conf = o
    except requests.exceptions.RequestException:
        print("Couldn't get data from", add)

    if conf is None:
        return False

    url = f"{add}/xui/inbound/update/{id}"
    conf["userid"] = 0
    if action == 'enable':
        conf["enable"] = "true"
    elif action == 'disable':
        conf["enable"] = "false"

    s = ''
    for k, v in conf.items():
        s += k+'='+parse.quote(str(v))+'&'

    try:
        res = requests.post(url, headers=headers, data=s)
        return res.json()['success']
    except:
        return False


if __name__ == '__main__':
    sk = "MTY4MzY3MzE4NXxEdi1CQkFFQ180SUFBUkFCRUFBQVpmLUNBQUVHYzNSeWFXNW5EQXdBQ2t4UFIwbE9YMVZUUlZJWWVDMTFhUzlrWVhSaFltRnpaUzl0YjJSbGJDNVZjMlZ5XzRNREFRRUVWWE5sY2dIX2hBQUJBd0VDU1dRQkJBQUJDRlZ6WlhKdVlXMWxBUXdBQVFoUVlYTnpkMjl5WkFFTUFBQUFHdi1FRndFQ0FRVmhaRzFwYmdFTFUyOVViMjl1TXpWaGJtY0F8m4s6TS3qj6Z5tM9s1HcXZOtNChEMbtrT3RJOljqp7yw="
    disable_enable_xui_config("185.104.189.187", sk, 11, 'disable')
