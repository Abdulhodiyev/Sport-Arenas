from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.bookings.models import Booking, BookingStatus


class PaymentStatus(models.TextChoices):
    CREATED = "created", "Created"
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class PaymentMethod(models.TextChoices):
    CLICK = "click", "Click"
    PAYME = "payme", "Payme"
    CARD = "card", "Card"   # future
    CASH = "cash", "Cash"   # offline


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="UZS")
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    provider_transaction_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.CREATED)
    metadata = models.JSONField(null=True, blank=True)  # store raw provider payload if needed

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["provider_transaction_id"]),
            models.Index(fields=["status"]),
        ]

    def mark_success(self, provider_id=None, payload=None):
        self.status = PaymentStatus.SUCCESS
        if provider_id:
            self.provider_transaction_id = provider_id
        if payload:
            self.metadata = payload
        self.verified_at = timezone.now()
        self.save()

        # agar booking biriktirilgan bo'lsa, uni paid deb belgilang
        if self.booking:
            self.booking.status = BookingStatus.APPROVED if self.booking.status == BookingStatus.PENDING else self.booking.status
            # booking uchun maydon total_price dan farq bo'lsa ham to'lov bajarildi deb qabul qilamiz
            self.booking.save()

    def mark_failed(self, payload=None):
        self.status = PaymentStatus.FAILED
        if payload:
            self.metadata = payload
        self.save()

    def mark_refunded(self, payload=None):
        self.status = PaymentStatus.REFUNDED
        if payload:
            self.metadata = payload
        self.save()

    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency} - {self.status}"
