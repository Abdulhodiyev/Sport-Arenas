from django.db import models
from django.conf import settings


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SportType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Arena(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="arenas"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="arenas")
    sport_type = models.ForeignKey(SportType, on_delete=models.CASCADE, related_name="arenas")

    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ArenaImage(models.Model):
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="arenas/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.arena.name}"


class WorkingHours(models.Model):
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name="working_hours")
    day_of_week = models.IntegerField(choices=[
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ])
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        unique_together = ("arena", "day_of_week")

    def __str__(self):
        return f"{self.get_day_of_week_display()} — {self.open_time} / {self.close_time}"


class   PriceTable(models.Model):
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name="prices")
    day_type = models.CharField(max_length=20, choices=[
        ("weekday", "Weekday"),
        ("weekend", "Weekend")
    ])
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("arena", "day_type")

    def __str__(self):
        return f"{self.arena.name} – {self.day_type}: {self.price_per_hour} UZS"


class Review(models.Model):
    arena = models.ForeignKey(
        Arena,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="arena_reviews"
    )
    rating = models.PositiveSmallIntegerField()  # 1–5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("arena", "user")  # 1 user → 1 review per arena
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.arena.name} review by {self.user.username}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_arenas"
    )
    arena = models.ForeignKey(
        Arena,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "arena")

    def __str__(self):
        return f"{self.user.username} → {self.arena.name}"
