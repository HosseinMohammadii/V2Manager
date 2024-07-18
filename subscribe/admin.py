from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db import models
from django.forms import Textarea, TextInput, NumberInput

from payment.admin import PaymentInline
from utils.size import pretty_megabyte, pretty_byte
from .models import Subscription, MiddleServer, Link, Server
from .tasks import check_and_disable_subs, update_traffic


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
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
        models.FloatField: {'widget': NumberInput(attrs={'size': 6})},
    }


@admin.action(description="Update Subs Status And Action")
def update_status_and_action(modeladmin, request, queryset):
    dis_subs = check_and_disable_subs(queryset)
    msg = ""
    for s in dis_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "disabled"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="Update Traffic")
def update_traffic_action(modeladmin, request, queryset):
    dis_subs = update_traffic(queryset)
    msg = ""
    for s in dis_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "updated"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="Enable Configs")
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


@admin.action(description="Reset Used Traffic")
def reset_traffic(modeladmin, request, queryset):
    enabled_subs = []
    for sub in queryset:
        sub.reset_traffic()
        enabled_subs.append(sub)
    msg = ""
    for s in enabled_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "reset traffic"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="Update all Subs Status And Action")
def update_status_of_all(modeladmin, request, queryset):
    qs = Subscription.objects.all()
    update_status_and_action(modeladmin, request, qs)


@admin.action(description="Set one month From Today")
def set_expire_date_next_month(modeladmin, request, queryset):
    edited_subs = []
    for sub in queryset:
        sub.set_expire_date_next_month()
        edited_subs.append(sub)
    msg = ""
    for s in edited_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "edited"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="Renew Reset+1M+Enable")
def renew(modeladmin, request, queryset):
    edited_subs = []
    for sub in queryset:
        sub.set_expire_date_next_month()
        sub.reset_traffic()
        sub.enable()
        sub.add_last_payment()
        edited_subs.append(sub)
    msg = ""
    for s in edited_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "edited"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="Disable")
def disable(modeladmin, request, queryset):
    edited_subs = []
    for sub in queryset:
        sub.disable()
        sub.update_status_disable()
        edited_subs.append(sub)
    msg = ""
    for s in edited_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "edited"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.action(description="Add Last Payment Again")
def add_last_payment(modeladmin, request, queryset):
    edited_subs = []
    for sub in queryset:
        sub.add_last_payment()
        edited_subs.append(sub)
    msg = ""
    for s in edited_subs:
        msg += f"  subs id: {s.id} of {s.user_name}  -"
    msg += "added last payment"

    modeladmin.message_user(
        request,
        msg,
    )


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        '__str__',
        'status',
        'brief_description',
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
    search_fields = ['id', 'user_name', 'description']
    inlines = [LinkInline, PaymentInline]
    actions = [update_status_and_action, update_status_of_all, update_traffic_action, enable_all_configs, reset_traffic, set_expire_date_next_month,
               renew, disable, add_last_payment]


@admin.register(FastSubscription)
class FastSubscriptionAdmin(ModelAdmin):
    list_display = (
        'id',
        'user_name',
        'brief_description',
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

    list_filter = ['status']

    # readonly_fields = ('link',)
    inlines = [LinkInline, PaymentInline]
    actions = [update_status_and_action, update_traffic_action, update_status_of_all, enable_all_configs, reset_traffic, set_expire_date_next_month,
               renew, disable, add_last_payment]

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["pre_used_traffic"].widget = NumberInput(attrs={'size': 18})
        return form

    def pretty_remained_traffic(self, instance):
        return pretty_megabyte(instance.lazy_remained_megabytes)

    def pretty_last_used_traffic(self, instance):
        return pretty_byte(instance.last_used_traffic)


@admin.register(MiddleServer)
class MiddleServerAdmin(ModelAdmin):
    list_display = ('__str__', 'port', 'server_type', 'active')
    list_editable = ('active',)
