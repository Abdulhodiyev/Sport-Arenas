from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):

    def _create_user(self, username, password=None, **extra_fields):
        # Django avtomatik ravishda email yuboradi → Uni olib tashlaymiz
        extra_fields.pop("email", None)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # create_superuser ham email yuboradi → olib tashlaymiz
        extra_fields.pop("email", None)

        return self._create_user(username=username, password=password, **extra_fields)


class User(AbstractUser):
    email = None  # remove email field completely

    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    is_blocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["phone"]

    objects = CustomUserManager()

    def __str__(self):
        return self.username
