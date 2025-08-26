from celery import shared_task
from django.utils import timezone

from .utils import notify_user
from .models import Notification
from django.contrib.auth.models import User
from orders.models import Order


@shared_task
def send_digest_task(days: int = 1):
    from datetime import timedelta

    since = timezone.now() - timedelta(days=days)
    for user in User.objects.all():
        orders = Order.objects.filter(user=user, created_at__gte=since)
        if not orders.exists():
            continue
        total_spend = sum([o.total_amount for o in orders])
        msg_lines = [
            f"Hi {user.username}, here is your last {days}-day summary:",
            f"Total orders: {orders.count()}",
            f"Total spend: {total_spend}",
        ]
        notify_user(user, title="Your FarmFresh digest", message="\n".join(msg_lines), sms=False)



