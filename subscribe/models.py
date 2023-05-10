import base64
import uuid

import requests
from django.conf import settings
from django.db import models

from django.contrib.auth.models import User

from utils.marzban import get_marzban_traffic
from utils.uri import get_original_confs_from_subscription, get_edited_confs
from utils.xui import get_xui_traffic


class LinkTypes(models.TextChoices):
    URI = 'URI', 'URI'
    SUBSCRIPTION_LINK = 'Subscription_Link', 'Subscription_Link'
    ENCODED = 'Encoded', 'Encoded'
    CLASH = 'Clash', 'Clash'
    URI_LIST = 'URI_List', 'URI_List'


class PanelTypes(models.TextChoices):
    XUI = "XUI", "XUI"
    MARZBAN = 'Marzban', 'Marzban'


class Server(models.Model):
    add = models.CharField(max_length=128, null=True, blank=True)
    host = models.CharField(max_length=128, null=True, blank=True)
    port = models.CharField(max_length=16, default=54321)
    auth = models.CharField(max_length=512, null=True, blank=True)
    panel = models.CharField(max_length=16, choices=PanelTypes.choices, default=PanelTypes.MARZBAN)

    def __str__(self):
        return ":".join((str(self.add), self.port))

    def __repr__(self):
        return self.__str__()


class Link(models.Model):
    subscription = models.ForeignKey("Subscription", on_delete=models.CASCADE)
    config_id = models.CharField(max_length=256, null=True, blank=True, help_text="for xui links")
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True, )
    value = models.TextField()
    type = models.CharField(max_length=64, choices=LinkTypes.choices, default=LinkTypes.SUBSCRIPTION_LINK)


class Subscription(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    identifier = models.UUIDField(default=uuid.uuid4, editable=True)
    user_name = models.CharField(max_length=256)
    traffic = models.IntegerField(default=0, help_text="In gigabytes")
    expire_date = models.DateField(null=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ' - '.join((self.user_name, str(self.id)))

    @property
    def link(self):
        return settings.SERVER_ADDRESS + "subs/land/" + str(self.identifier)

    def get_traffic(self):
        tr = 0
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.SUBSCRIPTION_LINK:
                tr += get_marzban_traffic(l.value)

            if l.server.panel == PanelTypes.XUI:
                tr += get_xui_traffic(l.server.add, l.server.port, l.server.auth, l.config_id)

        return tr
    @property
    def get_original_confs(self) -> list:
        all = []
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.SUBSCRIPTION_LINK:
                all += get_original_confs_from_subscription(l.value)
            if l.server.panel == PanelTypes.XUI and l.type == LinkTypes.URI:
                all.append(l.value)
        return all

    def get_edited_confs(self):
        mss = []
        qs = MiddleServer.objects.filter(active=True)
        for ms in qs:
            mss.append((ms.address, ms.port))
        marzban_visited_servers = []
        all = []
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.SUBSCRIPTION_LINK and l.server.id not in marzban_visited_servers:
                original_confs = get_original_confs_from_subscription(l.value)
                if len(original_confs) == 0:
                    continue
                edited_confs = get_edited_confs(original_confs, mss)
                all += original_confs + edited_confs
                marzban_visited_servers.append(l.server.id)

            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.URI_LIST and l.server.id not in marzban_visited_servers:
                original_confs = list(filter(lambda x: len(x) > 0, l.value.split("\n")))
                if len(original_confs) == 0:
                    continue
                edited_confs = get_edited_confs(original_confs, mss)
                all += original_confs + edited_confs
                marzban_visited_servers.append(l.server.id)

            if l.server.panel == PanelTypes.XUI and l.type == LinkTypes.URI:
                all.append(l.value)
        return all

    def get_edited_confs_uri(self):
        all = self.get_edited_confs()
        # for oo in all:
        #     print(oo)
        return base64.b64encode('\n'.join(all).encode('ascii'))


class MiddleServer(models.Model):
    address = models.CharField(max_length=128)
    port = models.CharField(max_length=16)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.address + ' - ' + str(self.id)
