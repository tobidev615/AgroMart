from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import Produce
from notifications.utils import notify_user
from orders.models import OrderItem


@receiver(post_save, sender=Produce)
def notify_produce_available(sender, instance: Produce, created: bool, **kwargs):
    # Notify the farmer when produce becomes available again
    if not created and instance.available and instance.farmer and instance.farmer.user:
        notify_user(
            instance.farmer.user,
            title="Produce available",
            message=f"Your produce '{instance.name}' is now marked as available.",
        )
        # Notify recent customers (last 30 days) that this produce is fresh again
        since = timezone.now() - timedelta(days=30)
        recent_buyer_ids = (
            OrderItem.objects.filter(produce=instance, order__created_at__gte=since)
            .values_list("order__user_id", flat=True)
            .distinct()
        )
        for user_id in recent_buyer_ids:
            try:
                user = instance.farmer.user.__class__.objects.get(id=user_id)
                notify_user(
                    user,
                    title="Fresh harvest available",
                    message=f"{instance.name} is fresh and available again from {instance.farmer.name}.",
                )
            except Exception:
                pass

