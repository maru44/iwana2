from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=254, write_only=True)

    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "picture",
            "name",
            "email",
            "intro",
            "is_superuser",
            "password",
        ]

    def create(self, password, validated_data):
        user = User.objects.create_user(password=password, **validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["pk", "username", "picture", "name", "email", "intro", "is_superuser"]
