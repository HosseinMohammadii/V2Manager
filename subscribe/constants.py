from django.db import models


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
