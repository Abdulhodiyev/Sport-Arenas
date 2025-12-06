from django.urls import path
from .views import RegisterView, MeView, UserListView, UserDetailView, LogoutView

app_name = 'users'

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("users/me/", MeView.as_view()),
    path("users/", UserListView.as_view()),
    path("users/<int:pk>/", UserDetailView.as_view()),
]
