from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    arena_name = serializers.CharField(source="arena.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "user", "arena", "arena_name",
            "date", "start_time", "end_time",
            "status", "total_price", "created_at"
        ]
        read_only_fields = ["status", "user", "total_price"]


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["arena", "date", "start_time", "end_time"]

    def create(self, validated_data):
        user = self.context["request"].user
        booking = Booking.objects.create(user=user, **validated_data)
        return booking