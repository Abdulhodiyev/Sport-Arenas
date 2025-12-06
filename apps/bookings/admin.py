# apps/bookings/admin.py
from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "arena", "date", "start_time", "end_time", "status", "total_price")
    list_filter = ("status", "arena", "date")
    search_fields = ("user__username", "arena__name")
