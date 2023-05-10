import base64
import json

import requests

from urllib.parse import unquote, quote


def get_original_confs_from_subscription(link, ) -> list:
    try:
        res = requests.get(link)
        conf_text = res.text
        decoded = base64.b64decode(conf_text).decode('ascii')
        return decoded.split('\n')
    except requests.RequestException:
        print("Can not get conf from subscription link")
        return []


def get_edited_confs(confs: list, servers: list):
    added_props = set()
    produced = []
    conf: str
    for conf in confs:
        # print(conf)
        if conf.find('vmess://') > -1:
            dconf = get_vmess_dict(conf.replace("vmess://", ""))
            prop_key = "vmess_" + dconf['net']
            if prop_key in added_props:
                continue
            for serv, port in servers:
                dconf = get_vmess_dict(conf.replace("vmess://", ""))
                smid = int(len(serv) / 2)
                serv_id = '_'.join((serv[:2], serv[smid - 1:smid + 1], serv[-2:]))
                dconf["add"] = serv
                dconf["port"] = port
                dconf["ps"] += " Depart " + serv_id
                added_props.add(prop_key)
                produced.append("vmess://" + str(get_vmess_uri(dconf)))

        if conf.find('vless://') > -1:
            dconf = get_vless_dict(conf.replace("vless://", ""))
            prop_key = "vless_" + dconf['type']
            if prop_key in added_props:
                continue
            for serv, port in servers:
                dconf = get_vless_dict(conf.replace("vless://", ""))
                smid = int(len(serv) / 2)
                serv_id = '_'.join((serv[:2], serv[smid - 1:smid + 1], serv[-2:]))
                dconf["add"] = serv
                dconf["port"] = port
                if dconf.get("serviceName", None) is not None:
                    dconf["serviceName"] += " Depart " + serv_id
                else:
                    dconf["path"] += " Depart " + serv_id
                added_props.add(prop_key)
                produced.append("vless://" + get_vless_uri(dconf))

        if conf.find('trojan://') > -1:
            dconf = get_trojan_dict(conf.replace("trojan://", ""))
            prop_key = "trojan_" + dconf['type']
            if prop_key in added_props:
                continue
            for serv, port in servers:
                dconf = get_trojan_dict(conf.replace("trojan://", ""))
                smid = int(len(serv) / 2)
                # serv_id = '_'.join((serv[:2], serv[smid - 1:smid + 1], serv[-2:]))
                serv_id = " Delaydar"
                dconf["add"] = serv
                dconf["port"] = port
                if dconf.get("serviceName", None) is not None:
                    dconf["serviceName"] += " Depart " + serv_id
                else:
                    dconf["path"] += " Depart " + serv_id
                added_props.add(prop_key)
                # print(dconf)
                produced.append("trojan://" + get_trojan_uri(dconf))
    # print(added_props)
    return produced


def get_trojan_dict(uri: str):
    d = dict()
    parts = uri.split('?')
    d['password'] = parts[0].split('@')[0]
    d['add'] = parts[0].split('@')[1].split(':')[0]
    d['port'] = parts[0].split('@')[1].split(':')[1]
    extras = parts[1].split('&')
    for ex in extras:
        key = ex.split('=')[0]
        value = ex.split('=')[1]
        d[key] = value

    if d.get('serviceName', None) is not None:
        t = d['serviceName'].split("#")
        d["realName"] = unquote(t[1])
        d['serviceName'] = t[0]
    else:
        t = d['path'].split("#")
        d["realName"] = unquote(t[1])
        d['path'] = t[0]
    return d


def get_trojan_uri(d: dict):
    if d.get('serviceName', None) is not None:
        d['serviceName'] = d['serviceName'] + "#" + quote(d['realName'])
    else:
        d['path'] = d['path'] + "#" + quote(d['realName'])

    del(d['realName'])

    base = f"{d['password']}@{d['add']}:{d['port']}"
    del (d['password'])
    del (d['add'])
    del (d['port'])
    extras = ''
    for k, v in d.items():
        extras += f"&{k}={v}"
    extras = extras[1:]
    extras = '?' + extras
    return base + extras


def get_vless_dict(uri: str):
    d = dict()
    parts = uri.split('?')
    d['password'] = parts[0].split('@')[0]
    d['add'] = parts[0].split('@')[1].split(':')[0]
    d['port'] = parts[0].split('@')[1].split(':')[1]
    extras = parts[1].split('&')
    for ex in extras:
        key = ex.split('=')[0]
        value = ex.split('=')[1]
        d[key] = value

    return d


def get_vless_uri(d: dict):
    base = f"{d['password']}@{d['add']}:{d['port']}"
    del (d['password'])
    del (d['add'])
    del (d['port'])
    extras = ''
    for k, v in d.items():
        extras += f"&{k}={v}"
    extras = extras[1:]
    extras = '?' + extras
    return base + extras


def get_vmess_dict(uri: str):
    d = json.loads(base64.b64decode(uri).decode('ascii'))
    return d


def get_vmess_uri(d: dict):
    t = (json.dumps(d, indent='', ).replace(', ', ',')).encode('ascii')
    return base64.b64encode(t).decode('ascii')


if __name__ == '__main__':
    trojans = [
        "trojan://hsITmEQiHPjVJ9AV1k4Jhg@realshop.novationmarket.com:443?security=tls&type=ws&host=&sni=realshop.novationmarket.com&headerType=&path=%2Ftw#%F0%9F%8F%82%20Fr1%20%5BTrojan%20ws%5D",

        "trojan://hsITmEQiHPjVJ9AV1k4Jhg@bitcoin.cashypto.com:443?security=tls&type=ws&host=&sni=realshop.novationmarket.com&headerType=&path=%2Ftw#%F0%9F%8F%82%20Fr1-MCI1%20%5BTrojan%20ws%5D",
        "trojan://hsITmEQiHPjVJ9AV1k4Jhg@dogecoin.cashypto.com:443?security=tls&type=ws&host=&sni=realshop.novationmarket.com"
        "&headerType=&path=%2Ftw#%F0%9F%8F%82%20Fr1-Irancell1%20%5BTrojan%20ws%5D",
        "trojan://hsITmEQiHPjVJ9AV1k4Jhg@realshop.novationmarket.com:443?security=tls&type=grpc&host=&sni=realshop.novationmarket.com&headerType=&serviceName=tg#%F0%9F%8F%82%20Fr1%20%5BTrojan%20grpc%5D",
        "trojan://hsITmEQiHPjVJ9AV1k4Jhg@bitcoin.cashypto.com:443?security=tls&type=grpc&host=&sni=realshop.novationmarket.com&headerType=&serviceName=tg#%F0%9F%8F%82%20Fr1-MCI1%20%5BTrojan%20grpc%5D",
        "trojan://hsITmEQiHPjVJ9AV1k4Jhg@dogecoin.cashypto.com:443?security=tls&type=grpc&host=&sni=realshop.novationmarket.com&headerType=&serviceName=tg#%F0%9F%8F%82%20Fr1-Irancell1%20%5BTrojan%20grpc%5D=", ]
    for trj in trojans:
        print('\n')
        print(trj)
        trojan_d = get_trojan_dict(trj)
        print(trojan_d)
        trojan_uri = get_trojan_uri(trojan_d)
        print(trojan_uri)
        trojan_d = get_trojan_dict(trojan_uri)
        print(trojan_d)
