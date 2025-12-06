from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PaymentViewSet, payment_webhook, click_webhook

router = DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", payment_webhook, name="payments-webhook"),
    path("webhook/click/", click_webhook),
]
