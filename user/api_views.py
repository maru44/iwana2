from django.shortcuts import get_object_or_404
from user.models import User
from rest_framework import views, status, permissions, response
from .serializers import *

import jwt

class ProfileAPIView(views.APIView):
    def get_object(self, request):
        try:
            token = self.request.get('iwana_user_token')
            payload = jwt.decode(token, None, None)
            user = User.objects.get(id=payload['user_id'])
            
