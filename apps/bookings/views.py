from datetime import datetime

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking, BookingStatus
from .serializers import BookingSerializer, BookingCreateSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related("arena", "user")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create"]:
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        """
        Foydalanuvchi faqat o‘z bookinglarini ko‘radi.
        Admin — hammani ko‘radi.
        """
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save()

    # ------------- ACTIONS ------------- #

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status not in [BookingStatus.PENDING, BookingStatus.APPROVED]:
            return Response({"error": "Bu bookingni bekor qilib bo‘lmaydi."}, status=400)

        booking.status = BookingStatus.CANCELED
        booking.save()
        return Response({"message": "Booking bekor qilindi."})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        booking = self.get_object()

        if booking.status != BookingStatus.PENDING:
            return Response({"error": "Faqat pending booking tasdiqlanadi."}, status=400)

        booking.status = BookingStatus.APPROVED
        booking.save()
        return Response({"message": "Booking tasdiqlandi."})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        booking = self.get_object()

        if booking.status != BookingStatus.PENDING:
            return Response({"error": "Faqat pending booking rad etiladi."}, status=400)

        booking.status = BookingStatus.REJECTED
        booking.save()
        return Response({"message": "Booking rad etildi."})

    @action(detail=False, methods=["get"], url_path="calendar/(?P<arena_id>[^/.]+)")
    def calendar(self, request, arena_id=None):
        """
        Arena uchun band qilingan vaqtlar ro‘yxatini beradi.
        """
        bookings = Booking.objects.filter(
            arena_id=arena_id,
            status__in=[BookingStatus.PENDING, BookingStatus.APPROVED]
        ).order_by("date", "start_time")

        data = BookingSerializer(bookings, many=True).data
        return Response(data)

    @action(detail=False, methods=["get"], url_path="free_slots/(?P<arena_id>[^/.]+)")
    def free_slots(self, request, arena_id=None):
        """
        Berilgan arena va sana uchun bo'sh vaqtlarni qaytaradi.
        """
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "date parametri majburiy. Masalan: ?date=2025-12-12"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return Response({"error": "date formati noto'g'ri. YYYY-MM-DD bo'lishi kerak."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Arena olish
        from apps.arenas.models import Arena, WorkingHours
        try:
            arena = Arena.objects.get(id=arena_id)
        except Arena.DoesNotExist:
            return Response({"error": "Arena topilmadi."}, status=404)

        weekday = date_obj.weekday()
        working_hours = arena.working_hours.filter(day_of_week=weekday).first()

        if not working_hours:
            return Response({
                "date": date_str,
                "free_slots": [],
                "message": "Bu kunda arena ishlamaydi."
            })

        open_time = working_hours.open_time
        close_time = working_hours.close_time

        # Band bookinglar
        bookings = arena.bookings.filter(
            date=date_obj,
            status__in=[BookingStatus.PENDING, BookingStatus.APPROVED]
        ).order_by("start_time")

        # --- BO'SH INTERVALLARNI HISOBLASH --- #
        free_slots = []

        current_start = open_time

        for b in bookings:
            if current_start < b.start_time:
                free_slots.append([str(current_start), str(b.start_time)])
            current_start = max(current_start, b.end_time)

        # bandlar tugagandan keyin oxirgi segment
        if current_start < close_time:
            free_slots.append([str(current_start), str(close_time)])

        return Response({
            "date": date_str,
            "working_hours": [str(open_time), str(close_time)],
            "free_slots": free_slots
        })
