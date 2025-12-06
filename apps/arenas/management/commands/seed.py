# apps/arenas/management/commands/seed.py
from django.core.management.base import BaseCommand
from apps.arenas.models import City, SportType

class Command(BaseCommand):
    help = "Seed initial cities and sports"

    def handle(self, *args, **options):
        cities = ["Tashkent", "Samarkand", "Bukhara"]
        sports = ["Football", "Tennis", "Basketball"]
        for c in cities:
            City.objects.get_or_create(name=c)
        for s in sports:
            SportType.objects.get_or_create(name=s)
        self.stdout.write(self.style.SUCCESS("Seeded cities and sports"))
