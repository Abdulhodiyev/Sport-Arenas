from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.bookings.models import Booking
from .models import Notification


@receiver(post_save, sender=Booking)
def booking_status_change(sender, instance, created, **kwargs):
    if not created and instance.status in ["approved", "rejected"]:
        Notification.objects.create(
            user=instance.user,
            title=f"Your booking was {instance.status}",
            message=f"Arena: {instance.arena.name}\nDate: {instance.date}"
        )
