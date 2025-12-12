# core/urls.py (yoki project router)
from django.http import HttpResponse
from django.urls import path, include
from apps.payments.views import click_webhook, payment_webhook
from rest_framework.routers import DefaultRouter
from apps.payments.views import PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/payments/webhook/', payment_webhook, name='payment-webhook'),
    path('api/payments/click-webhook/', click_webhook, name='click-webhook'),
    # optional: fake pay page for manual simulation
    path('api/payments/fake-pay/<int:payment_id>/', lambda r, payment_id: HttpResponse("fake pay page")),
]
