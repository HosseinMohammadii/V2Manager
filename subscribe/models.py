import base64
import datetime
import uuid

import requests
from django.conf import settings
from django.db import models

from django.contrib.auth.models import User

from utils.cache import get_marzban_cached_token
from utils.marzban import get_marzban_traffic, disable_enable_marzban_config, get_marzban_traffic_from_api, \
    get_marzban_subs_url
from utils.size import gigabyte_to_megabyte, byte_to_megabyte
from utils.uri import get_original_confs_from_subscription, get_edited_confs
from utils.xui import get_xui_traffic, disable_enable_xui_config


class LinkTypes(models.TextChoices):
    URI = 'URI', 'URI'
    SUBSCRIPTION_LINK = 'Subscription_Link', 'Subscription_Link'
    ENCODED = 'Encoded', 'Encoded'
    CLASH = 'Clash', 'Clash'
    URI_LIST = 'URI_List', 'URI_List'
    BY_CONFIG_ID = 'By Config ID', 'By Config ID'


class PanelTypes(models.TextChoices):
    XUI = "XUI", "XUI"
    MARZBAN = 'Marzban', 'Marzban'
    XUI_3 = "XUI 3", "XUI 3"


class SubscriptionStatuses(models.TextChoices):
    ACTIVE = "Active", "Active"
    TIME_EXPIRED = "Time Expired", "Time Expired"
    TRAFFIC_EXPIRED = "Traffic Expired", "Traffic Expired"
    DISABLED = "Disabled", "Disabled"


class Server(models.Model):
    add = models.CharField(max_length=128, null=True, blank=True)
    host = models.CharField(max_length=128, null=True, blank=True)
    port = models.CharField(max_length=16, default=54321)
    auth = models.CharField(max_length=512, null=True, blank=True)
    panel = models.CharField(max_length=16, choices=PanelTypes.choices, default=PanelTypes.MARZBAN)
    panel_add = models.URLField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=16, null=True, blank=True)
    password = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return ":".join((str(self.add), self.port))

    def __repr__(self):
        return self.__str__()


class Link(models.Model):
    subscription = models.ForeignKey("Subscription", on_delete=models.CASCADE)
    config_id = models.CharField(max_length=256, null=True, blank=True, help_text="for xui links")
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True, )
    value = models.TextField()
    type = models.CharField(max_length=64, choices=LinkTypes.choices, default=LinkTypes.BY_CONFIG_ID)


    def get_marzban_confs_by_config_id(self):
        url = get_marzban_subs_url(self.server.panel_add, get_marzban_cached_token(self.server),
                                   self.config_id, )
        url = self.server.panel_add + url
        return get_original_confs_from_subscription(url)


class Subscription(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    identifier = models.UUIDField(default=uuid.uuid4, editable=True)
    user_name = models.CharField(max_length=256)
    traffic = models.IntegerField(default=0, help_text="In gigabytes")
    expire_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=SubscriptionStatuses.choices, default=SubscriptionStatuses.ACTIVE,
                              max_length=32)

    def __str__(self):
        return ' - '.join((self.user_name, str(self.id)))

    @property
    def link(self):
        return settings.SERVER_ADDRESS + "subs/land/" + str(self.identifier)

    @property
    def remained_days(self):
        if self.expire_date is None:
            return 100
        d = (self.expire_date - datetime.date.today()).days
        return d

    @property
    def remained_megabytes(self):
        if self.traffic == 0:
            return 10000
        d = gigabyte_to_megabyte(self.traffic) - byte_to_megabyte(self.get_used_traffic())
        return int(d)

    def get_used_traffic(self):
        tr = 0
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:
                tr += get_marzban_traffic_from_api(l.server.panel_add, get_marzban_cached_token(l.server),
                                                   l.config_id, )

            if l.server.panel == PanelTypes.XUI:
                tr += get_xui_traffic(l.server.panel_add, l.server.auth, l.config_id)

        return tr

    def disable(self):
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:
                disable_enable_marzban_config(l.server.panel_add, get_marzban_cached_token(l.server),
                                              l.config_id, "disable")
            if l.server.panel == PanelTypes.XUI:
                disable_enable_xui_config(l.server.panel_add, l.server.auth,
                                          l.config_id, "disable")

    def update_status_active(self):
        self.status = SubscriptionStatuses.ACTIVE
        self.save()

    def update_status_dis_time(self):
        self.status = SubscriptionStatuses.TIME_EXPIRED
        self.save()

    def update_status_dis_traffic(self):
        self.status = SubscriptionStatuses.TRAFFIC_EXPIRED
        self.save()

    def update_status_disable(self):
        self.status = SubscriptionStatuses.DISABLED
        self.save()

    @property
    def get_original_confs(self) -> list:
        all = []
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:
                all += l.get_marzban_confs_by_config_id()
            if l.server.panel == PanelTypes.XUI and l.type == LinkTypes.URI:
                all.append(l.value)
        return all

    def get_edited_confs(self):
        mss = []
        qs = MiddleServer.objects.filter(active=True)
        for ms in qs:
            mss.append((ms.address, ms.port, ms.id))
        marzban_visited_servers = []
        all = []
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID and\
                    l.server.id not in marzban_visited_servers:

                original_confs = l.get_marzban_confs_by_config_id()
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
