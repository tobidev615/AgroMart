from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from deliveries.models import Delivery
from .models import AuditLog

@receiver(post_save, sender=Order)
def audit_order_status(sender, instance: Order, created, **kwargs):
    if not created:
        AuditLog.objects.create(
            user=instance.user,
            action='order.status.changed',
            object_type='Order',
            object_id=str(instance.id),
            metadata={'status': instance.status}
        )

@receiver(post_save, sender=Delivery)
def audit_delivery_status(sender, instance: Delivery, created, **kwargs):
    if not created:
        user = getattr(getattr(instance, 'distributor', None), 'user', None)
        AuditLog.objects.create(
            user=user,
            action='delivery.status.changed',
            object_type='Delivery',
            object_id=str(instance.id),
            metadata={'status': instance.status}
        )


