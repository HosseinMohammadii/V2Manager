import requests


def get_marzban_traffic(subs_url, ):
    url = subs_url + '/info'
    try:
        res = requests.get(url)
        data = res.json()
        return data['used_traffic']
    except requests.exceptions.ConnectionError:
        return 0
