from rest_framework import serializers
from .models import *
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'name', 'picture', 'intro', 'is_superuser']

class PlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plat
        fields = ['name']

class WantedSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    user_pk = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    plat = PlatSerializer(many=True, read_only=True)
    class Meta:
        model = Wanted
        fields = [
            'slug', 'want_name', 'posted', 'is_gotten', 'want_intro', 'user_pk',
            'want_price', 'user', 'plat', 'is_accept_official', 'picture',
        ]

    def create(self, validated_data):
        validated_data['user'] = validated_data.get('user_pk', None)

        if validated_data['user'] is None:
            raise serializers.ValidationError('user not found')
        del validated_data['user_pk']

        return Wanted.objects.create(**validated_data)

class OfferSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Offer
        fields = [
            'offer_url', 'user', 'posted', 'wanted', 'is_noticed'
        ]
