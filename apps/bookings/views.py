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
        serializer.save(user=self.request.user)

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
