from rest_framework import serializers
from .models import *
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'name', 'picture']

class PlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plat
        fields = ['name']

class WantedSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    plat = PlatSerializer(many=True, read_only=True)
    class Meta:
        model = Wanted
        fields = [
            'slug', 'want_name', 'posted', 'is_gotten', 'want_intro',
            'want_price', 'user', 'plat', 'is_accept_official', 'picture',
        ]

class OfferSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Offer
        fields = [
            'offer_url', 'user', 'posted', 'wanted', 'is_noticed'
        ]
