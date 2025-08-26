from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User

from orders.models import Order
from notifications.utils import notify_user


class Command(BaseCommand):
    help = "Send digest emails to users summarizing recent orders"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Number of days to look back")

    def handle(self, *args, **options):
        days = options["days"]
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
        self.stdout.write(self.style.SUCCESS("Digest sent"))



