from django.contrib.admin import ModelAdmin, register, TabularInline
from django.db import models
from django.forms import Textarea, NumberInput

from .models import Payment


@register(Payment)
class PaymentModelAdmin(ModelAdmin):
    list_display = ['id', 'subscription', 'amount', 'done']
    readonly_fields = ['created', 'updated']
    autocomplete_fields = ['subscription']
    list_filter = ['done']

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["amount"].widget = NumberInput(attrs={'size': 10})
        return form


class PaymentInline(TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created', 'updated']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 50})},
        models.BigIntegerField: {'widget': NumberInput(attrs={'size': 16})},
        models.IntegerField: {'widget': NumberInput(attrs={'size': 16})}
    }



