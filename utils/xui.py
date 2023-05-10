import requests


def get_xui_traffic(add, port, auth, id):
    url = f"http://{add}:{port}/xui/inbound/list"
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
        return 0
