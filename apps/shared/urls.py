from django.urls import path
from .views import (
    FileUploadView,
    NotificationListView,
    mark_as_read,
    healthcheck
)

urlpatterns = [
    path("upload/", FileUploadView.as_view()),
    path("notifications/", NotificationListView.as_view()),
    path("notifications/<int:pk>/read/", mark_as_read),
    path("healthcheck/", healthcheck),
]
