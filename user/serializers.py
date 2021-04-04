from .models import User
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'username', 'picture', 'name', 'email', 'intro', 'is_superuser',
        ]