from django.contrib import admin
from django.contrib.admin import ModelAdmin

from utils.size import pretty_megabyte, pretty_byte
from .models import Subscription, MiddleServer, Link, Server
from .tasks import check_and_disable_subs


class FastSubscription(Subscription):
    class Meta:
        proxy = True


@admin.register(Server)
class ServerAdmin(ModelAdmin):
    filter_horizontal = ('middle_servers',)
    pass


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1


@admin.action(description="update subs status and action if needed")
def update_status(modeladmin, request, queryset):
    dis_subs = check_and_disable_subs(queryset)
    msg = ""
    for s in dis_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "disabled"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="enable configs")
def enable_all_configs(modeladmin, request, queryset):
    enabled_subs = []
    for sub in queryset:
        sub.enable()
        enabled_subs.append(sub)
    msg = ""
    for s in enabled_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "enabled"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="make used traffic zero")
def zero_traffic(modeladmin, request, queryset):
    enabled_subs = []
    for sub in queryset:
        sub.zero_traffic()
        enabled_subs.append(sub)
    msg = ""
    for s in enabled_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "reset traffic"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="update ALL subs status and action if needed")
def update_status_of_all(modeladmin, request, queryset):
    qs = Subscription.objects.all()
    update_status(modeladmin, request, qs)


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        '__str__',
        'status',
        'remained_days',
        'last_used_traffic',
        'last_check_time',
    )
    readonly_fields = (
        'link',
        'get_original_confs',
        'get_edited_confs',
        'remained_days',
        'realtime_remained_megabytes',
        'last_check_time',
    )
    inlines = [LinkInline]
    actions = [update_status, update_status_of_all]


@admin.register(FastSubscription)
class FastSubscriptionAdmin(ModelAdmin):
    list_display = (
        '__str__',
        # 'link',
        'status',
        'remained_days',
        'pretty_remained_traffic',
        'pretty_last_used_traffic',
        'last_check_time',
    )
    readonly_fields = (
        'link',
        'remained_days',
        'last_used_traffic',
        'pretty_last_used_traffic',
        'pretty_remained_traffic',
        'last_check_time',
    )
    # readonly_fields = ('link',)
    inlines = [LinkInline]
    actions = [update_status, update_status_of_all, enable_all_configs]

    def pretty_remained_traffic(self, instance):
        return pretty_megabyte(instance.lazy_remained_megabytes)

    def pretty_last_used_traffic(self, instance):
        return pretty_byte(instance.last_used_traffic)


@admin.register(MiddleServer)
class MiddleServerAdmin(ModelAdmin):
    list_display = ('__str__', 'port', 'server_type', 'active')
