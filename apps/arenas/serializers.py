from rest_framework import serializers
from .models import City, SportType, Arena, ArenaImage, WorkingHours, PriceTable, Review, Favorite


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name"]


class SportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportType
        fields = ["id", "name"]


class ArenaImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArenaImage
        fields = ["id", "image", "is_main"]


class WorkingHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = WorkingHours
        fields = ["id", "day_of_week", "day_name", "open_time", "close_time"]


class PriceTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceTable
        fields = ["id", "day_type", "price_per_hour"]


class ArenaSerializer(serializers.ModelSerializer):
    images = ArenaImageSerializer(many=True, read_only=True)
    working_hours = WorkingHoursSerializer(many=True, read_only=True)
    prices = PriceTableSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    sport_type = SportTypeSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Arena
        fields = [
            "id", "name", "description", "city", "sport_type",
            "address", "latitude", "longitude", "rating",
            "images", "working_hours", "prices",
            "is_favorite",
            "created_at", "updated_at"
        ]

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False



class ArenaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arena
        fields = [
            "name", "description",
            "city", "sport_type",
            "address", "latitude", "longitude"
        ]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "arena", "user", "rating", "comment", "created_at"]
        read_only_fields = ["user", "arena", "created_at"]

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    arena_name = serializers.CharField(source="arena.name", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "arena", "arena_name", "created_at"]
        read_only_fields = ["arena_name", "created_at"]
