import base64
import json

import requests

from urllib.parse import unquote, quote


def convert_net(val):
    if val == 'ws':
        return 'ws'
    elif val == 'grpc':
        return 'grpc'


def convert_protocol(val):
    if val == 'trojan':
        return 'tr'
    elif val == 'vmess':
        return 'vm'
    elif val == 'vless':
        return 'vl'
    raise ValueError


def is_applicable(protocol, net, apply_on_str):
    if apply_on_str is None or len(apply_on_str) < 2:
        return True
    apply_on_list = apply_on_str.split(",")
    for apply_on in apply_on_list:
        if protocol+'-'+net in apply_on:
            return True
    return False


def get_original_confs_from_subscription(link, ) -> list:
    try:
        res = requests.get(link)
        conf_text = res.text
        decoded = base64.b64decode(conf_text).decode('ascii')
        return decoded.split('\n')
    except requests.RequestException:
        print("Can not get conf from subscription link", link)
        return []


def just_rename_configs(configs, base_remark, end_remark):
    end_remark = '' if end_remark is None else end_remark

    produced = []
    for config in configs:
        if config.find('vmess://') > -1:
            dconf = get_vmess_dict(config.replace("vmess://", ""))
            dconf["ps"] = ' '.join((base_remark, dconf["ps"], end_remark))
            produced.append("vmess://" + str(get_vmess_uri(dconf)))

        elif config.find('vless://') > -1:
            dconf = get_vless_dict(config.replace("vless://", ""))
            dconf["realName"] = ' '.join((base_remark, dconf["realName"], end_remark))
            produced.append("vless://" + get_vless_uri(dconf))

        elif config.find('trojan://') > -1:
            dconf = get_trojan_dict(config.replace("trojan://", ""))
            dconf["realName"] = ' '.join((base_remark, dconf["realName"], end_remark))
            produced.append("trojan://" + get_trojan_uri(dconf))

    return produced


# servers format :  list of (ms.address, ms.port, ms.id, ms.vmess_extra_config, ms.vless_extra_config,
# ms.trojan_extra_config, ms.remark, base_remark)
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
            for serv, port, ms_id, vmess_ec, vless_ec, trojan_ec, remark, base_remark, end_remark, apply_on in servers:
                dconf = get_vmess_dict(conf.replace("vmess://", ""))
                if not is_applicable(convert_protocol('vmess'), convert_net(dconf['net']), apply_on):
                    continue
                dconf["add"] = serv
                dconf["port"] = port
                dconf["ps"] = ' '.join((base_remark, dconf["ps"], remark))
                if vmess_ec is not None:
                    dconf.update(vmess_ec)
                added_props.add(prop_key)
                produced.append("vmess://" + str(get_vmess_uri(dconf)))

        if conf.find('vless://') > -1:
            dconf = get_vless_dict(conf.replace("vless://", ""))
            prop_key = "vless_" + dconf['type']
            if prop_key in added_props:
                continue
            for serv, port, ms_id, vmess_ec, vless_ec, trojan_ec, remark, base_remark, end_remark, apply_on in servers:
                dconf = get_vless_dict(conf.replace("vless://", ""))
                if not is_applicable(convert_protocol('vless'), convert_net(dconf['type']), apply_on):
                    continue
                dconf["add"] = serv
                dconf["port"] = port
                dconf["realName"] = ' '.join((base_remark, dconf["realName"], end_remark, remark))
                if vless_ec is not None:
                    dconf.update(vless_ec)
                added_props.add(prop_key)
                produced.append("vless://" + get_vless_uri(dconf))

        if conf.find('trojan://') > -1:
            dconf = get_trojan_dict(conf.replace("trojan://", ""))
            prop_key = "trojan_" + dconf['type']
            if prop_key in added_props:
                continue
            for serv, port, ms_id, vmess_ec, vless_ec, trojan_ec, remark, base_remark, end_remark, apply_on in servers:
                dconf = get_trojan_dict(conf.replace("trojan://", ""))
                if not is_applicable(convert_protocol('trojan'), convert_net(dconf['type']), apply_on):
                    continue
                dconf["add"] = serv
                dconf["port"] = port
                dconf["realName"] = ' '.join((base_remark, dconf["realName"], end_remark, remark))

                if trojan_ec is not None:
                    dconf.update(trojan_ec)
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

    del (d['realName'])

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

    if d.get('serviceName', None) is not None:
        t = d['serviceName'].split("#")
        d["realName"] = unquote(t[1])
        d['serviceName'] = t[0]
    else:
        t = d['path'].split("#")
        d["realName"] = unquote(t[1])
        d['path'] = t[0]

    return d


def get_vless_uri(d: dict):
    if d.get('serviceName', None) is not None:
        d['serviceName'] = d['serviceName'] + "#" + quote(d['realName'])
    else:
        d['path'] = d['path'] + "#" + quote(d['realName'])

    del (d['realName'])

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


def get_vmess_dict(uri: str) -> dict:
    d = json.loads(base64.b64decode(uri).decode('ascii'))
    return d


def get_vmess_uri(d: dict):
    t = (json.dumps(d, indent='', ).replace(', ', ',')).encode('ascii')
    return base64.b64encode(t).decode('ascii')


if __name__ == '__main__':
    # trojans = [
    #     "trojan://hsITmEQiHPjVJ9AV1k4Jhg@realshop.novationmarket.com:443?security=tls&type=ws&host=&sni=realshop.novationmarket.com&headerType=&path=%2Ftw#%F0%9F%8F%82%20Fr1%20%5BTrojan%20ws%5D",
    #
    #     "trojan://hsITmEQiHPjVJ9AV1k4Jhg@bitcoin.cashypto.com:443?security=tls&type=ws&host=&sni=realshop.novationmarket.com&headerType=&path=%2Ftw#%F0%9F%8F%82%20Fr1-MCI1%20%5BTrojan%20ws%5D",
    #     "trojan://hsITmEQiHPjVJ9AV1k4Jhg@dogecoin.cashypto.com:443?security=tls&type=ws&host=&sni=realshop.novationmarket.com"
    #     "&headerType=&path=%2Ftw#%F0%9F%8F%82%20Fr1-Irancell1%20%5BTrojan%20ws%5D",
    #     "trojan://hsITmEQiHPjVJ9AV1k4Jhg@realshop.novationmarket.com:443?security=tls&type=grpc&host=&sni=realshop.novationmarket.com&headerType=&serviceName=tg#%F0%9F%8F%82%20Fr1%20%5BTrojan%20grpc%5D",
    #     "trojan://hsITmEQiHPjVJ9AV1k4Jhg@bitcoin.cashypto.com:443?security=tls&type=grpc&host=&sni=realshop.novationmarket.com&headerType=&serviceName=tg#%F0%9F%8F%82%20Fr1-MCI1%20%5BTrojan%20grpc%5D",
    #     "trojan://hsITmEQiHPjVJ9AV1k4Jhg@dogecoin.cashypto.com:443?security=tls&type=grpc&host=&sni=realshop.novationmarket.com&headerType=&serviceName=tg#%F0%9F%8F%82%20Fr1-Irancell1%20%5BTrojan%20grpc%5D=", ]
    # for trj in trojans:
    #     print('\n')
    #     print(trj)
    #     trojan_d = get_trojan_dict(trj)
    #     print(trojan_d)
    #     trojan_uri = get_trojan_uri(trojan_d)
    #     print(trojan_uri)
    #     trojan_d = get_trojan_dict(trojan_uri)
    #     print(trojan_d)
    vm_sample = "ewogICJ2IjogIjIiLAogICJwcyI6ICJzNyIsCiAgImFkZCI6ICJwYW5lbDF4LmlyZG9tYWluLmxpbmsiLAogICJwb3J0IjogMjYzMjAsCiAgImlkIjogIjg3Y2EyZDFkLTQ4ZDAtNDBmOS05YmJjLWZmYWE0YWYyY2EwNSIsCiAgImFpZCI6IDAsCiAgIm5ldCI6ICJ3cyIsCiAgInR5cGUiOiAibm9uZSIsCiAgImhvc3QiOiAiIiwKICAicGF0aCI6ICIvUXhJRldsa3pQT3puLyIsCiAgInRscyI6ICJub25lIgp9"
    print(get_vmess_dict(vm_sample))

    vl_sample = "81b9eea8-7cef-4cdc-f50e-fd783fe8ee27@panel1x.irdomain.link:41916?type=ws&security=none&path=%2FgVqoJjnYByWz%2F#s27%20khoshnoodF"
    print(get_vless_dict(vl_sample))
