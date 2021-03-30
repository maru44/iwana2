from .models import User
from rest_framework import serializers

class ProfileSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'username', 'picture', 'name', 'email', 'intro', 'is_superuser',
        ]