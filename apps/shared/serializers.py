from rest_framework import serializers
from .models import Notification


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "is_read", "created_at"]
