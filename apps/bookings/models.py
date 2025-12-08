from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.arenas.models import Arena
from datetime import datetime, time


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELED = "canceled", "Canceled"
    COMPLETED = "completed", "Completed"


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    arena = models.ForeignKey(
        Arena,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- VALIDATION ---- #

    def clean(self):
        # vaqt to‘g‘ri kelishi kerak
        if self.start_time >= self.end_time:
            raise ValidationError("Boshlanish vaqti tugash vaqtidan oldin bo‘lishi shart.")

        # arena ishlaydigan vaqt ichida bo‘lishi kerak
        weekday = self.date.weekday()
        working_hours = self.arena.working_hours.filter(day_of_week=weekday).first()

        if not working_hours:
            raise ValidationError("Bu kunda arena ishlamaydi.")

        if not (working_hours.open_time <= self.start_time < working_hours.close_time):
            raise ValidationError("Arena bu vaqtda ishlamaydi.")

        # boshqa bronlar bilan to‘qnashmasligi kerak
        overlapping = Booking.objects.filter(
            arena=self.arena,
            date=self.date,
            status__in=[BookingStatus.APPROVED, BookingStatus.PENDING]
        ).exclude(id=self.id).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        if overlapping.exists():
            raise ValidationError("Bu vaqt allaqachon band qilingan.")

    # narx hisoblash
    def calculate_price(self):
        weekday = self.date.weekday()
        day_type = "weekday" if weekday < 5 else "weekend"

        price = self.arena.prices.filter(day_type=day_type).first()
        if price:
            # davomiylikni hisoblash
            duration = (
                    datetime.combine(self.date, self.end_time) -
                    datetime.combine(self.date, self.start_time)
            )

            # float emas, Decimal bo‘lishi shart!
            hours = Decimal(duration.total_seconds()) / Decimal(3600)

            # narxni hisoblash (Decimal * Decimal)
            self.total_price = price.price_per_hour * hours
