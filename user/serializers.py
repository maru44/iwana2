from .models import User
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=254, write_only=True)
    class Meta:
        model = User
        fields = [
            'pk', 'username', 'picture', 'name', 'email', 'intro', 'is_superuser', 'password'
        ]

    def create(self, password, validated_data):
        user = User.objects.create_user(password=password, **validated_data)
        return user

    """
    def validate_email(self, email):
        email = email
        if User.objects.filter(email=email, is_active=False).exists():
            User.objects.filter(email=email, is_active=False).delete()
            return email

    def validate_username(self, username):
        username = username
        User.objects.filter(username=username, is_active=False).delete()
        return username
    """
