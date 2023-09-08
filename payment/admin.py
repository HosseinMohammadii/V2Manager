from django.contrib.admin import ModelAdmin, register, TabularInline

from .models import Payment


@register(Payment)
class PaymentModelAdmin(ModelAdmin):
    list_display = ['id', 'subscription', 'amount', 'done']
    readonly_fields = ['created', 'updated']
    autocomplete_fields = ['subscription']


class PaymentInline(TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created', 'updated']



