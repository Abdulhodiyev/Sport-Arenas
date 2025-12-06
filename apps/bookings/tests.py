from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.arenas.models import Arena
from .models import Booking
from datetime import date, time

User = get_user_model()

class BookingRaceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass123456")
        self.arena = Arena.objects.create(
            name="Test Arena",
            slug="test-arena",
            sport_type="football",
            price_per_hour=50.0
        )

    def test_double_booking_prevented(self):
        Booking.objects.create(
            user=self.user,
            arena=self.arena,
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status=Booking.STATUS_CONFIRMED
        )
        # try create overlapping booking
        with self.assertRaises(Exception):
            Booking.objects.create(
                user=self.user,
                arena=self.arena,
                date=date.today(),
                start_time=time(10, 30),
                end_time=time(11, 30),
                status=Booking.STATUS_CONFIRMED
            )
