import base64
import json

import requests


def get_original_confs(link, ) -> list:
    res = requests.get(link)
    conf_text = res.text
    decoded = base64.b64decode(conf_text).decode('ascii')
    return decoded.split('\n')


def get_edited_confs(confs:list, servers: list):
    added_props = set()
    produced = []
    conf: str
    for conf in confs:
        # print(conf)
        if conf.find('vmess://') > -1:
            dconf = get_vmess_dict(conf.replace("vmess://", ""))
            prop_key = "vmess_"+dconf['net']
            if prop_key in added_props:
                continue
            for serv, port in servers:
                smid = int(len(serv)/2)
                serv_id = ':'.join((serv[:2], serv[smid-1:smid+1], serv[-2:]))
                dconf["add"] = serv
                dconf["port"] = port
                dconf["ps"] += " Depart"+serv_id
                added_props.add(prop_key)
                produced.append("vmess://"+str(get_vmess_uri(dconf)))
                
        if conf.find('vless://') > -1:
            dconf = get_vless_dict(conf.replace("vless://", ""))
            prop_key = "vless_"+dconf['type']
            if prop_key in added_props:
                continue
            for serv, port in servers:
                smid = int(len(serv)/2)
                serv_id = ':'.join((serv[:2], serv[smid-1:smid+1], serv[-2:]))
                dconf["add"] = serv
                dconf["port"] = port
                try:
                    dconf["serviceName"] += "Depart" + serv_id
                except:
                    pass
                try:
                    dconf["path"] += "Depart" + serv_id
                except:
                    pass
                added_props.add(prop_key)
                produced.append("vless://"+get_vless_uri(dconf))
                
        if conf.find('trojan://') > -1:
            dconf = get_trojan_dict(conf.replace("trojan://", ""))
            prop_key = "trojan_"+dconf['type']
            if prop_key in added_props:
                continue
            for serv, port in servers:
                smid = int(len(serv)/2)
                serv_id = ':'.join((serv[:2], serv[smid-1:smid+1], serv[-2:]))
                dconf["add"] = serv
                dconf["port"] = port
                try:
                    dconf["serviceName"] += "Depart"+serv_id
                except:
                    pass
                try:
                    dconf["path"] += "Depart" + serv_id
                except:
                    pass
                added_props.add(prop_key)
                produced.append("trojan://"+get_trojan_uri(dconf))
    print(added_props)
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

    return d


def get_trojan_uri(d: dict):
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
    return base64.b64encode(t)
