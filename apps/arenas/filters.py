import django_filters
from .models import Arena
from django.db.models import Min


class ArenaFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(method="filter_min_price")
    max_price = django_filters.NumberFilter(method="filter_max_price")
    available_date = django_filters.DateFilter(method="filter_available")

    class Meta:
        model = Arena
        fields = ["city", "sport_type"]

    def filter_min_price(self, queryset, name, value):
        return queryset.filter(prices__price_per_hour__gte=value)

    def filter_max_price(self, queryset, name, value):
        return queryset.filter(prices__price_per_hour__lte=value)

    def filter_available(self, queryset, name, value):
        # Arenala shu kunda band bo'lmagan va shu kunda ishlaydigan bo'lishi kerak
        # Step 1: ishlaydigan maydonlar
        weekday = value.weekday()
        working = queryset.filter(working_hours__day_of_week=weekday)

        # Step 2: shu kunda band bo'lgan arenalar
        from apps.bookings.models import Booking, BookingStatus
        busy = Booking.objects.filter(
            date=value,
            status__in=[BookingStatus.PENDING, BookingStatus.APPROVED]
        ).values_list("arena_id", flat=True)

        # Step 3: busy bo'lmagan arenalar
        return working.exclude(id__in=busy)
