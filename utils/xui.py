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
        s += k + '=' + parse.quote(str(v)) + '&'

    try:
        res = requests.post(url, headers=headers, data=s)
        return res.json()['success']
    except:
        return False


def zero_traffic_xui_config(add, auth, id, action: str):
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
    conf["up"] = 0
    conf["down"] = 0
    del(conf["id"])
    del(conf['tag'])

    s = ''
    for k, v in conf.items():
        s += k + '=' + parse.quote(str(v)) + '&'

    try:
        res = requests.post(url, headers=headers, data=s)
        return res.json()['success']
    except:
        return False

def xui_nginx_ws_creator(l: list):
    # list of path and port
    for path, port in l:
        s = """
    location /{PATH}/ { # Consistent with the path of V2Ray configuration
    if ($http_upgrade != "websocket") { # Return 404 error when WebSocket upgrading negotiate failed
        return 404;
    }
    proxy_redirect off;
    proxy_pass http://127.0.0.1:{PORT}; # Assume WebSocket is listening at localhost on port of 10000
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    # Show real IP in v2ray access.log
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }"""
        s = s.replace("{PORT}", str(port)).replace("{PATH}", str(path))
        print(s)


if __name__ == '__main__':
    # sk = "MTY4MzY3MzE4NXxEdi1CQkFFQ180SUFBUkFCRUFBQVpmLUNBQUVHYzNSeWFXNW5EQXdBQ2t4UFIwbE9YMVZUUlZJWWVDMTFhUzlrWVhSaFltRnpaUzl0YjJSbGJDNVZjMlZ5XzRNREFRRUVWWE5sY2dIX2hBQUJBd0VDU1dRQkJBQUJDRlZ6WlhKdVlXMWxBUXdBQVFoUVlYTnpkMjl5WkFFTUFBQUFHdi1FRndFQ0FRVmhaRzFwYmdFTFUyOVViMjl1TXpWaGJtY0F8m4s6TS3qj6Z5tM9s1HcXZOtNChEMbtrT3RJOljqp7yw="
    # disable_enable_xui_config("185.104.189.187", sk, 11, 'disable')
    a = [
        ('moPBBtwQuVDF', 56823),
        ('HFEzKofYkNiP', 46530),
        ('neICEQmhCpdX', 35250),
        ('JptWGcQnNKqM', 18648),
        ('gVqoJjnYByWz', 41916),
        ('chdDPsRAWNEi', 53686),
        ('QxIFWlkzPOzn', 26320),
        ('dJGuUgtAZdxs', 35617),
        ('AhuwiPmHjXwG', 48789),
        ('LpLUadBVKekQ', 20118),
        ('pOUsJXQfvpFO', 50610),
        ('TbyjXcCFQGrk', 28588),
    ]
    xui_nginx_ws_creator(a)
