from django.contrib import admin
from .models import Arena, City, SportType, ArenaImage, WorkingHours, PriceTable

@admin.register(Arena)
class ArenaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "city", "sport_type", "is_active", "rating", "created_at")
    list_filter = ("city", "sport_type", "is_active")
    search_fields = ("name", "address", "owner__username")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("owner",)
    inlines = []  # optionally add image inline

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(SportType)
class SportTypeAdmin(admin.ModelAdmin):
    search_fields = ("name",)
