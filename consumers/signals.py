from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from userprofiles.models import UserType

from .models import ConsumerProfile, ConsumerAnalytics, ConsumerPreference


@receiver(post_save, sender=User)
def create_consumer_profile(sender, instance, created, **kwargs):
    """Create consumer profile when a user with CONSUMER role is created."""
    if created and hasattr(instance, 'profile'):
        if instance.profile.role == UserType.CONSUMER:
            ConsumerProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=ConsumerProfile)
def create_consumer_analytics_and_preferences(sender, instance, created, **kwargs):
    """Create analytics and preferences when consumer profile is created."""
    if created:
        # Create analytics
        ConsumerAnalytics.objects.get_or_create(consumer=instance)
        
        # Create preferences
        ConsumerPreference.objects.get_or_create(consumer=instance)


@receiver(post_save, sender=User)
def update_consumer_profile_on_role_change(sender, instance, **kwargs):
    """Update consumer profile when user role changes."""
    if hasattr(instance, 'profile'):
        if instance.profile.role == UserType.CONSUMER:
            ConsumerProfile.objects.get_or_create(user=instance)
        else:
            # If role is not CONSUMER, delete consumer profile if it exists
            ConsumerProfile.objects.filter(user=instance).delete()


