from django.shortcuts import get_object_or_404
from user.models import User
from rest_framework import views, status, permissions, response
from .serializers import *
from django.conf import settings

import jwt

class ProfileAPIView(views.APIView):
    def get_object(self, request, token):
        try:
            # token = self.request.get('iwana_user_token')
            payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            return User.objects.get(id=payload['user_id'])
        except jwt.ExpiredSignatureError as e:
            return response.Response({'error': 'Activations link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            return response.Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, token, format=None):
        user = self.get_object(token)
        serializer = ProfileSerialzier(user)
        return response.Response(serializer.data)
