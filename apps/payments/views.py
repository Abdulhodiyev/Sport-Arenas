from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Payment, PaymentStatus
from .serializers import PaymentCreateSerializer, PaymentSerializer

# NOTE: provider integration functions (pseudo) — implement provider SDK / HTTP calls in services module.
# at top of apps.payments.views
from .services import create_click_payment, verify_provider_payment, refund_provider_payment, verify_click_signature



class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related("user", "booking")
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action in ["create"]:
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save()
        provider_resp = create_click_payment(payment)
        if provider_resp.get("provider_id"):
            payment.provider_transaction_id = provider_resp["provider_id"]
            payment.metadata = provider_resp.get("metadata", {})
            payment.status = "pending"
            payment.save()
            # If you want to include pay_url in response we can set it on serializer.context
            self._last_pay_url = provider_resp.get("pay_url")
        else:
            payment.status = "failed"
            payment.metadata = provider_resp
            payment.save()
        return payment

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        # attach pay_url if available
        pay_url = getattr(self, "_last_pay_url", None)
        if pay_url:
            resp.data["pay_url"] = pay_url
        return resp

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.status != PaymentStatus.SUCCESS:
            return Response({"error": "Only successful payments can be refunded."}, status=400)

        # call provider refund
        resp = refund_provider_payment(payment)
        if resp.get("success"):
            payment.mark_refunded(payload=resp)
            return Response({"message": "Refund initiated."})
        return Response({"error": "Refund failed", "detail": resp}, status=400)


# --- Webhook endpoint: provider'll call this when payment status changes --- #
@api_view(["POST"])
@permission_classes([permissions.AllowAny])  # providers won't have JWT
def payment_webhook(request):
    """
    Generic webhook handler. Provider signature verification must be implemented.
    Expected payload depends on provider (Click, Payme).
    """
    payload = request.data

    # verify signature (implement in services)
    valid = verify_provider_payment(payload)
    if not valid.get("valid"):
        return Response({"detail": "Invalid signature"}, status=400)

    provider_id = valid.get("provider_id")
    status = valid.get("status")  # provider-specific status mapping
    payment = get_object_or_404(Payment, provider_transaction_id=provider_id)

    if status == "success":
        payment.mark_success(provider_id=provider_id, payload=payload)
    elif status in ["failure", "error"]:
        payment.mark_failed(payload=payload)
    # else: other statuses we ignore or log

    return Response({"ok": True})


@extend_schema(tags=["Payments"])
@api_view(["POST"])
@permission_classes([permissions.AllowAny])  # Click cannot authenticate
def click_webhook(request):
    payload = request.data

    # 1. Signature verify
    if not verify_click_signature(payload):
        return Response({"error": "Invalid signature"}, status=400)

    # 2. Payment ID from payload
    payment_id = payload.get("merchant_trans_id")
    payment = get_object_or_404(Payment, id=payment_id)

    # 3. Success
    if payload.get("error") == "0":
        payment.mark_success(
            provider_id=payload["transaction_id"],
            payload=payload
        )
        return Response({"status": "success"})

    # 4. Failed
    else:
        payment.mark_failed(payload)
        return Response({"status": "failed"})
