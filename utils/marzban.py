import json

import requests


def get_marzban_token(add, username, password):
    url = f"{add}/api/admin/token"
    d = f"grant_type=&username={username}&password={password}&scope=&client_id=&client_secret="
    headers = {'accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(url, headers=headers, data=d)
    return res.json()["access_token"]


def get_marzban_traffic(subs_url, ):
    url = subs_url + '/info'
    try:
        res = requests.get(url)
        data = res.json()
        return data['used_traffic']
    except requests.exceptions.ConnectionError:
        return 0


def get_marzban_traffic_from_api(add, auth, id):
    url = f"{add}/api/user/{id}"

    headers = {
        "Authorization": "Bearer " + auth,
        "Accept": "application/json",
    }
    res = requests.get(url, headers=headers)
    return res.json()["used_traffic"]


def get_marzban_subs_url(add, auth, id):
    url = f"{add}/api/user/{id}"

    headers = {
        "Authorization": "Bearer " + auth,
        "Accept": "application/json",
    }
    res = requests.get(url, headers=headers)
    return res.json()["subscription_url"]


def disable_enable_marzban_config(add, auth, id, action: str):
    url = f"{add}/api/user/{id}"

    headers = {
        "Authorization": "Bearer " + auth,
        "Accept": "application/json",
    }
    data = {}
    if action == 'disable':
        data["status"] = "disabled"
    if action == 'enable':
        data["status"] = "active"

    try:
        res = requests.put(url, headers=headers, data=json.dumps(data))
        return True
    except requests.exceptions.ConnectionError:
        return False


if __name__ == '__main__':
    # t = get_marzban_token("https://panel1.novationmarket.com", "hossein", "iran!123")
    t = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJob3NzZWluIiwiYWNjZXNzIjoic3VkbyIsImV4cCI6MTY4NDU3MzE2NX0.bwoZDrweaZRr9i_jesHzfn-aGZOXUVVsXeOkCUeVpnA"
    print("token", t)
    # disable_enable_marzban_config("realshop.novationmarket.com", t, "hooti", "disable")
    # ll = get_marzban_subs_url("https://panel1.novationmarket.com", t, "hooti",)
    # print(ll)

    ut = get_marzban_traffic_from_api("https://panel1.novationmarket.com", t, "nooshin",)
    print(ut)
