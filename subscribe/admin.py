from django.contrib import admin
from django.contrib.admin import ModelAdmin

from . models import Subscription, MiddleServer, Link, Server


@admin.register(Server)
class ServerAdmin(ModelAdmin):
    pass


class LinkInline(admin.TabularInline):
    model = Link

@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('__str__', 'link')
    readonly_fields = ('link', 'get_original_confs', 'get_edited_confs')
    # readonly_fields = ('link',)
    inlines = [LinkInline]


@admin.register(MiddleServer)
class MiddleServerAdmin(ModelAdmin):
    list_display = ('__str__', 'port', 'active')
