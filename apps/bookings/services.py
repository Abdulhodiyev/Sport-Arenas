from datetime import datetime, time, timedelta
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from apps.bookings.models import Booking

SLOT_MINUTES_DEFAULT = 60  # default slot size


def generate_time_slots(arena, slot_minutes=SLOT_MINUTES_DEFAULT):
    """
    Generate list of (start_time, end_time) tuples for one day according to arena open/close.
    Does NOT consider bookings — just raw slots.
    """
    slots = []
    cur = datetime.combine(datetime.today(), arena.open_time)
    close_dt = datetime.combine(datetime.today(), arena.close_time)
    delta = timedelta(minutes=slot_minutes)
    while cur + delta <= close_dt:
        start = cur.time()
        end = (cur + delta).time()
        slots.append((start, end))
        cur += delta
    return slots


def get_booked_intervals(arena, date):
    """Return list of (start_time, end_time) for confirmed/pending bookings on date"""
    qs = Booking.objects.filter(
        arena=arena, date=date, status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]
    ).values_list("start_time", "end_time")
    return list(qs)


def available_slots(arena, date, slot_minutes=SLOT_MINUTES_DEFAULT):
    """
    Produce available slots by excluding those that overlap with existing bookings.
    Overlap rule: slot_start < booking_end and slot_end > booking_start
    """
    all_slots = generate_time_slots(arena, slot_minutes=slot_minutes)
    booked = get_booked_intervals(arena, date)

    def overlaps(s, e, b_s, b_e):
        return (s < b_e) and (e > b_s)

    free = []
    for s, e in all_slots:
        conflict = False
        for b_s, b_e in booked:
            if overlaps(s, e, b_s, b_e):
                conflict = True
                break
        if not conflict:
            free.append({"start_time": s, "end_time": e})
    return free


def is_interval_available(arena, date, start_time, end_time):
    """Check if there is any overlapping booking for given interval."""
    return not Booking.objects.filter(
        arena=arena, date=date, status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]
    ).filter(
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    ).exists()


@transaction.atomic
def create_booking_atomic(user, arena, date, start_time, end_time, calculate_price_callable):
    """
    Atomic booking creation to avoid race conditions.
    - Optionally lock arena's bookings rows to ensure no concurrent insert clashes.
    """
    # Lock overlapping rows (if any) to prevent concurrent creates
    overlapping = Booking.objects.select_for_update().filter(
        arena=arena, date=date
    ).filter(
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    )

    if overlapping.exists():
        raise ValueError("Time slot is already booked")

    total_price = calculate_price_callable(arena, start_time, end_time)
    booking = Booking.objects.create(
        user=user,
        arena=arena,
        date=date,
        start_time=start_time,
        end_time=end_time,
        total_price=Decimal(total_price),
        status=Booking.STATUS_CONFIRMED,  # or pending depending on business
    )
    # Domain events, notifications, payment processing are triggered here (outside)
    return booking
