from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta

from subscribe.constants import SubscriptionStatuses
from subscribe.models import Subscription
from subscribe.tasks import check_and_disable_subs


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--time-buffer-minutes", action='store', type=int)
        parser.add_argument("--check-count", action='store', type=int)

    def handle(self, *args, **options):
        time_buffer_minutes = options["time_buffer_minutes"]
        check_count = options["check_count"]
        qs = Subscription.objects.filter(last_check_time__lte=datetime.now()-timedelta(minutes=time_buffer_minutes))
        qs = qs.filter(status=SubscriptionStatuses.ACTIVE)
        qs = qs[:check_count]
        disabled_subs = check_and_disable_subs(qs)
        for disabled_sub in disabled_subs:
            print(datetime.now(), disabled_sub.id, disabled_sub.user_name,
                  disabled_sub.description, disabled_sub.status)
