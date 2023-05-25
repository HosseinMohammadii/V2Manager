import datetime
import uuid

from django.conf import settings
from django.db import models

from django.contrib.auth.models import User

from subscribe.constants import LinkTypes, MiddleServerType, PanelTypes, SubscriptionStatuses
from subscribe.modelMixins import SubscriptionConfigMethodsMixin, SubscriptionTrafficMethodsMixin, \
    SubscriptionActionMethodsMixin
from utils.cache import get_marzban_cached_token
from utils.marzban import get_marzban_subs_url
from utils.uri import get_original_confs_from_subscription


class MiddleServer(models.Model):
    remark = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=128)
    port = models.CharField(max_length=16)
    active = models.BooleanField(default=True)
    server_type = models.CharField(max_length=32, choices=MiddleServerType.choices, default=MiddleServerType.FRAGMENT)
    vmess_extra_config = models.JSONField(max_length=512, null=True, blank=True)
    vless_extra_config = models.JSONField(max_length=512, null=True, blank=True)
    trojan_extra_config = models.JSONField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.address + ' - ' + str(self.id) + ' - ' + str(self.remark)


class Server(models.Model):
    remark = models.CharField(max_length=32, null=True, blank=True)
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

    def get_mss(self):  # suitable for edit confs functions
        mss = []
        for ms in self.middle_servers.filter(active=True):
            mss.append((ms.address, ms.port, ms.id,
                        ms.vmess_extra_config, ms.vmess_extra_config, ms.trojan_extra_config,
                        ms.remark, self.remark))
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


class Subscription(models.Model,
                   SubscriptionConfigMethodsMixin,
                   SubscriptionTrafficMethodsMixin,
                   SubscriptionActionMethodsMixin,
                   ):

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
    status = models.CharField(
        choices=SubscriptionStatuses.choices, default=SubscriptionStatuses.ACTIVE,
        max_length=32)

    last_used_traffic = models.IntegerField(
        default=0,
        help_text="The traffic used by user of current configs (pre used traffic is not included) and"
                  " will be updated everytime user requests or action call in admin page")

    pre_used_traffic = models.IntegerField(
        default=0,
        help_text="Used traffic that is not included in panels or a traffic volume that the corresponding config"
                  " is deleted")

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


