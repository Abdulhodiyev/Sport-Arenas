from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Arena, Review

@receiver([post_save, post_delete], sender=Review)
def update_arena_rating(sender, instance, **kwargs):
    arena = instance.arena
    avg_rating = arena.reviews.aggregate(avg=Avg("rating"))["avg"]
    arena.rating = avg_rating or 0
    arena.save()
