import base64
import datetime
import uuid

import requests
from django.conf import settings
from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

from subscribe.funcs import get_edited_confs_func
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


class MiddleServerType(models.TextChoices):
    ARVAN = "Arvan", "Arvan"
    CLOUDFLARE = "Cloudflare", "Cloudflare"
    FRAGMENT = "Fragment", "Fragment"


class PanelTypes(models.TextChoices):
    XUI = "XUI", "XUI"
    MARZBAN = 'Marzban', 'Marzban'
    XUI_3 = "XUI 3", "XUI 3"


class SubscriptionStatuses(models.TextChoices):
    ACTIVE = "Active", "Active"
    TIME_EXPIRED = "Time Expired", "Time Expired"
    TRAFFIC_EXPIRED = "Traffic Expired", "Traffic Expired"
    DISABLED = "Disabled", "Disabled"


class MiddleServer(models.Model):
    address = models.CharField(max_length=128)
    port = models.CharField(max_length=16)
    active = models.BooleanField(default=True)
    server_type = models.CharField(max_length=32, choices=MiddleServerType.choices, default=MiddleServerType.FRAGMENT)

    def __str__(self):
        return self.address + ' - ' + str(self.id)


class Server(models.Model):
    add = models.CharField(max_length=128, null=True, blank=True)
    host = models.CharField(max_length=128, null=True, blank=True)
    port = models.CharField(max_length=16, default=54321)
    auth = models.CharField(max_length=512, null=True, blank=True)
    panel = models.CharField(max_length=16, choices=PanelTypes.choices, default=PanelTypes.MARZBAN)
    panel_add = models.URLField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=16, null=True, blank=True)
    password = models.CharField(max_length=16, null=True, blank=True)

    middle_servers = models.ManyToManyField(MiddleServer)

    def __str__(self):
        return ":".join((str(self.add), self.port))

    def __repr__(self):
        return self.__str__()

    def get_mss(self): # suitable for edit confs functions
        mss = []
        for ms in self.middle_servers.filter(active=True):
            mss.append((ms.address, ms.port, ms.id))
        return mss


class Link(models.Model):
    subscription = models.ForeignKey("Subscription", on_delete=models.CASCADE)
    config_id = models.CharField(max_length=256, null=True, blank=True, help_text="for xui links")
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True, )
    value = models.TextField()
    type = models.CharField(max_length=64, choices=LinkTypes.choices, default=LinkTypes.BY_CONFIG_ID)
    include_original = models.BooleanField(default=False)


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
    last_used_traffic = models.IntegerField(default=0)
    last_check_time = models.DateTimeField(null=True, blank=True)

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
    def realtime_remained_megabytes(self):
        used_tr = self.get_used_traffic()
        self.update_used_traffic(used_tr)
        return self.remained_megabytes(used_tr)

    @property
    def lazy_remained_megabytes(self):
        return self.remained_megabytes(self.last_used_traffic)

    def remained_megabytes(self, used_tr):
        if int(self.traffic) == 0:
            d = 1024 * 60
        else:
            d = gigabyte_to_megabyte(self.traffic) - byte_to_megabyte(used_tr)
            d = int(d)
        return d

    def update_used_traffic(self, value):
        self.last_used_traffic = int(value)
        self.save()
        self.update_last_check_time()

    def update_last_check_time(self):
        self.last_check_time = timezone.now()
        self.save()

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
        ut = self.realtime_remained_megabytes  # just to update used traffic
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
        for l in self.link_set.filter(include_original=True):
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:
                all += l.get_marzban_confs_by_config_id()
            if l.server.panel == PanelTypes.XUI and l.type == LinkTypes.URI:
                all.append(l.value)
        return all

    def get_edited_confs(self):
        return get_edited_confs_func(self)

    def get_edited_confs_uri(self):
        all = self.get_edited_confs()
        # for oo in all:
        #     print(oo)
        return base64.b64encode('\n'.join(all).encode('ascii'))

    def get_all_confs_uri(self):
        a = self.get_original_confs
        a = a + self.get_edited_confs()
        return base64.b64encode('\n'.join(a).encode('ascii'))



