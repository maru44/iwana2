from rest_framework import serializers
from .models import *
from user.models import User

class WantedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wanted
        fields = ['slug', 'pk', 'is_accept_official']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'name', 'picture']

class OfferSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Offer
        fields = [
            'offer_url', 'user', 'posted', 'wanted', 'is_noticed'
        ]