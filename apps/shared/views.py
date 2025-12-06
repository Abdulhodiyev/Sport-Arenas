from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import UploadSerializer, NotificationSerializer
from .models import Notification
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data["file"]
            path = default_storage.save(f"uploads/{file.name}", ContentFile(file.read()))
            return Response({"file_url": default_storage.url(path)}, status=201)
        return Response(serializer.errors, status=400)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read(request, pk):
    try:
        notif = Notification.objects.get(id=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return Response({"message": "Notification marked as read"})
    except Notification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)


@api_view(["GET"])
def healthcheck(request):
    return Response({"status": "ok"})


