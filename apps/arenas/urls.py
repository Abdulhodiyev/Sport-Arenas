from rest_framework.routers import DefaultRouter
from .views import CityViewSet, SportTypeViewSet, ArenaViewSet

router = DefaultRouter()
router.register("cities", CityViewSet)
router.register("sports", SportTypeViewSet)
router.register("arenas", ArenaViewSet)

urlpatterns = router.urls
