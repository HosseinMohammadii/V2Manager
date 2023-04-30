from django.contrib import admin
from django.contrib.admin import ModelAdmin

from . models import Subscription, MiddleServer


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('__str__', 'link')


admin.site.register(MiddleServer)
