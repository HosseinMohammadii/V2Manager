from django.db import models
from django.contrib.auth.models import User

from subscribe.models import Subscription


class Payment(models.Model):
    subscription = models.ForeignKey(Subscription,  null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    done = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = 'created'



