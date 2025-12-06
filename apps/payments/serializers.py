from rest_framework import serializers
from .models import Payment, PaymentMethod, PaymentStatus


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["booking", "amount", "currency", "method"]

    def validate(self, attrs):
        # minimal validatsiya: amount > 0
        if attrs["amount"] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        payment = Payment.objects.create(user=user, **validated_data)
        # Bu yerda odatda provider API ga so'rov yuborib checkout link olamiz.
        return payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "booking", "user", "amount", "currency", "method",
            "status", "provider_transaction_id", "metadata",
            "created_at", "updated_at", "verified_at"
        ]
        read_only_fields = ["status", "provider_transaction_id", "metadata", "created_at", "updated_at", "verified_at"]
