from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["username", "phone", "password"]
        extra_kwargs = {
            "phone": {"required": True}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data.get("username"),
            phone=validated_data.get("phone")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "phone", "avatar",
            "first_name", "last_name",
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar", "phone"]