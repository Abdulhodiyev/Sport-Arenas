from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filters import ArenaFilter


from apps.arenas.models import (
    City, SportType, Arena, ArenaImage,
    WorkingHours, PriceTable, Review, Favorite
)
from .serializers import (
    CitySerializer, SportTypeSerializer,
    ArenaSerializer, ArenaCreateSerializer,
    ArenaImageSerializer, WorkingHoursSerializer,
    PriceTableSerializer, ReviewCreateSerializer, ReviewSerializer, FavoriteSerializer
)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]


class SportTypeViewSet(viewsets.ModelViewSet):
    queryset = SportType.objects.all()
    serializer_class = SportTypeSerializer
    permission_classes = [permissions.AllowAny]


class ArenaViewSet(viewsets.ModelViewSet):
    queryset = Arena.objects.all().select_related("city", "sport_type")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ArenaFilter
    search_fields = ["name", "description", "address"]
    ordering_fields = ["rating", "created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ArenaCreateSerializer
        return ArenaSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, pk=None):
        arena = self.get_object()
        serializer = ReviewCreateSerializer(data=request.data)

        if serializer.is_valid():
            # 1 user → 1 review
            Review.objects.update_or_create(
                arena=arena,
                user=request.user,
                defaults={
                    "rating": serializer.validated_data["rating"],
                    "comment": serializer.validated_data.get("comment", "")
                }
            )
            return Response({"message": "Review added successfully."}, status=201)

        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        arena = self.get_object()
        reviews = arena.reviews.all()
        data = ReviewSerializer(reviews, many=True).data
        return Response(data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        arena = self.get_object()
        fav, created = Favorite.objects.get_or_create(user=request.user, arena=arena)

        if created:
            return Response({"message": "Added to favorites"}, status=201)
        else:
            fav.delete()
            return Response({"message": "Removed from favorites"}, status=200)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def my_favorites(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related("arena")
        data = FavoriteSerializer(favorites, many=True).data
        return Response(data)

    # ---- ACTIONS ---- #

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def upload_image(self, request, pk=None):
        arena = self.get_object()
        image = request.FILES.get("image")

        if not image:
            return Response({"error": "Image is required"}, status=400)

        img = ArenaImage.objects.create(arena=arena, image=image)
        return Response(ArenaImageSerializer(img).data, status=201)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add_working_hours(self, request, pk=None):
        arena = self.get_object()
        serializer = WorkingHoursSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(arena=arena)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add_price(self, request, pk=None):
        arena = self.get_object()
        serializer = PriceTableSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(arena=arena)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    @action(detail=False, methods=["get"])
    def popular(self, request):
        arenas = Arena.objects.order_by("-rating")[:10]
        data = ArenaSerializer(arenas, many=True).data
        return Response(data)