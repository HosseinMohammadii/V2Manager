import base64
import uuid

import requests
from django.db import models

from subscribe.utils import get_original_confs, get_edited_confs


class Subscription(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=True)
    base_link1 = models.URLField(max_length=1024)
    base_link2 = models.URLField(max_length=1024, blank=True, null=True)
    base_link3 = models.URLField(max_length=1024, blank=True, null=True)
    user_name = models.CharField(max_length=256)

    def get_traffic(self):
        tr = 0
        if self.base_link1:
            res = requests.get(self.base_link1 + '/info')
            data = res.json()
            tr += data['used_traffic']

        if self.base_link2:
            res = requests.get(self.base_link2 + '/info')
            data = res.json()
            tr += data['used_traffic']

        if self.base_link3:
            res = requests.get(self.base_link3 + '/info')
            data = res.json()
            tr += data['used_traffic']

        return tr


    def get_original_confs(self) -> list:
        all = []
        if self.base_link1:
            all += get_original_confs(self.base_link1)
        if self.base_link2:
            all += get_original_confs(self.base_link2)
        if self.base_link3:
            all += get_original_confs(self.base_link3)
        return all

    def get_edited_confs(self):
        mss = []
        qs = MiddleServer.objects.all()
        for ms in qs:
            mss.append((ms.address, ms.port))
        all = []
        if self.base_link1:
            original_confs = get_original_confs(self.base_link1)
            edited_confs = get_edited_confs(original_confs, mss)
            print(edited_confs)
            all += original_confs+edited_confs
        if self.base_link2:
            all += get_original_confs(self.base_link2)
        if self.base_link3:
            all += get_original_confs(self.base_link3)
        return all

    def get_edited_confs_uri(self):
        all = self.get_edited_confs()
        # for oo in all:
        #     print(oo)
        return base64.b64encode('\n'.join(all).encode('ascii'))





class MiddleServer(models.Model):
    address = models.CharField(max_length=128)
    port = models.CharField(max_length=16)
