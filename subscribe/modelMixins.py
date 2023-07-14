import base64

from django.utils import timezone

from utils.cache import get_marzban_cached_token
from utils.marzban import get_marzban_traffic_from_api, disable_enable_marzban_config
from utils.size import gigabyte_to_megabyte, byte_to_megabyte
from utils.uri import get_original_confs_from_subscription, get_edited_confs, just_rename_configs
from utils.xui import get_xui_traffic, disable_enable_xui_config
from subscribe.constants import LinkTypes, MiddleServerType, PanelTypes, SubscriptionStatuses


class SubscriptionConfigMethodsMixin:
    @property
    def get_original_confs(self) -> list:
        all = []
        for l in self.link_set.filter(include_original=True):
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:

                all += just_rename_configs(l.get_marzban_confs_by_config_id(), l.server.remark)

            if l.server.panel == PanelTypes.XUI and l.type == LinkTypes.URI:
                all.append(just_rename_configs((l.value,), l.server.remark))

        return all

    def get_edited_confs(self):
        from subscribe.models import Subscription
        sub: Subscription
        all = []
        for l in self.link_set.all():
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:

                original_confs = l.get_marzban_confs_by_config_id()

                if len(original_confs) == 0:
                    continue

                edited_confs = get_edited_confs(original_confs, l.server.get_mss())
                all += edited_confs

            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.URI_LIST:

                original_confs = list(filter(lambda x: len(x) > 0, l.value.split("\n")))

                if len(original_confs) == 0:
                    continue

                edited_confs = get_edited_confs(original_confs, l.server.get_mss())
                all += edited_confs

            if l.server.panel == PanelTypes.XUI and l.type == LinkTypes.URI:
                edited_confs = get_edited_confs([l.value], l.server.get_mss())
                all += edited_confs

        return all

    def get_edited_confs_uri(self):
        all = self.get_edited_confs()
        # for oo in all:
        #     print(oo)
        return base64.b64encode('\n'.join(all).encode('ascii'))

    def get_all_confs_uri(self):
        a = self.get_original_confs
        a = a + self.get_edited_confs()
        return base64.b64encode('\n'.join(a).encode('ascii'))


class SubscriptionTrafficMethodsMixin:

    @property
    def realtime_remained_megabytes(self):
        used_tr = self.get_total_used_traffic()
        return self.remained_megabytes(used_tr)

    @property
    def lazy_remained_megabytes(self):
        return self.remained_megabytes(self.last_used_traffic + self.pre_used_traffic)

    def remained_megabytes(self, used_tr):
        """
        :param used_tr: in bytes
        :return: in megabytes
        """
        traffic = self.get_traffic_gb()

        d = gigabyte_to_megabyte(traffic) - byte_to_megabyte(used_tr)
        return d

    def update_last_used_traffic(self, value):
        self.last_used_traffic = int(value)
        self.save()
        self.update_last_check_time()

    def get_used_traffic(self) -> int:
        """
        get user current configs used traffic in bytes.
        :return:
        """
        from subscribe.models import Link
        def link_id(link: Link):
            return l.server.panel_add + l.config_id
        fetched_records = []
        tr = 0
        for l in self.link_set.all():

            if link_id(l) in fetched_records:
                continue

            amount = 0
            if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:
                amount = get_marzban_traffic_from_api(l.server.panel_add, get_marzban_cached_token(l.server),
                                                      l.config_id, )

            elif l.server.panel == PanelTypes.XUI:
                amount = get_xui_traffic(l.server.panel_add, l.server.auth, l.config_id)

            else:
                raise Exception(f"Link condition is not handled {l.server.panel_add} {l.type}")

            if amount > 0:
                fetched_records.append(link_id(l))
                tr += amount

        self.update_last_used_traffic(tr)
        return tr

    def get_total_used_traffic(self) -> int:
        """
        get user total used traffic in bytes. It means the pre_used_traffic + the current configs traffic
        :return:
        """
        tr = self.pre_used_traffic + self.get_used_traffic()
        return tr

    def get_traffic_gb(self):
        if int(self.traffic) == 0:
            return 50
        return self.traffic

    def get_traffic_text(self):
        if int(self.traffic) == 0:
            return " از نوع نامحدود"
        return "از نوع محدود"


class SubscriptionActionMethodsMixin:

    def update_last_check_time(self):
        self.last_check_time = timezone.now()
        self.save()

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
