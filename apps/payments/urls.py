# core/urls.py
from django.http import HttpResponse
from django.urls import path, include
from apps.payments.views import click_webhook, payment_webhook
from rest_framework.routers import DefaultRouter
from apps.payments.views import PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    # Webhooks MUST be ABOVE router
    path('api/payments/webhook/', payment_webhook, name='payment-webhook'),
    path('api/payments/click-webhook/', click_webhook, name='click-webhook'),

    # Optional fake pay page
    path('api/payments/fake-pay/<int:payment_id>/', lambda r, payment_id: HttpResponse("fake pay page")),

    # Router comes LAST
    path('api/', include(router.urls)),
]