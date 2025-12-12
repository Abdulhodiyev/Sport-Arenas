# apps/payments/serializers.py
from rest_framework import serializers
from .models import Payment

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["booking", "amount", "method"]  # user will be set from request

    def create(self, validated_data):
        user = self.context["request"].user
        payment = Payment.objects.create(user=user, **validated_data)
        return payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "booking", "user", "amount", "currency", "method",
                  "provider_transaction_id", "status", "metadata", "created_at"]
        read_only_fields = ["id", "user", "provider_transaction_id", "status", "metadata", "created_at"]
