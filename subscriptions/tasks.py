from datetime import timedelta, date

from celery import shared_task

from .models import Subscription, BillingPeriod


@shared_task
def run_subscription_cycle_task():
    today = date.today()
    subs = Subscription.objects.filter(is_active=True, next_delivery_date__lte=today)
    for sub in subs:
        delta = timedelta(days=7) if sub.plan.period == BillingPeriod.WEEKLY else timedelta(days=30)
        sub.next_delivery_date = today + delta
        sub.save(update_fields=["next_delivery_date"])





