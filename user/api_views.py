from django.shortcuts import get_object_or_404
from user.models import User
from rest_framework import views, status, permissions, response
from .serializers import *
from django.conf import settings
from django.http import JsonResponse, Http404

import jwt
import json, requests

from django.core import serializers

class UserInformationAPIView(views.APIView):
    def get_object(self, token_list):
        try:
            token = '.'.join(token_list)
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            # return User.objects.get(id=payload['user_id'])
            # return {"uid": payload['user_id']}
            return payload['user_id']
        except jwt.ExpiredSignatureError as e:
            return response.Response(serializers.serialize("json", {'error': 'Activations link expired'}), status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            return response.Response(serializers.serialize("json", {'error': 'Invalid Token'}), status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        head = request.GET.get("head")
        pay = request.GET.get("pay")
        signature = request.GET.get("signature")
        token_list = [head, pay, signature]
        
        #user_id = self.get_object(token_list)
        #data = {"uid": self.get_object(token_list)}
        # serializer = ProfileSerialzier(user)
        # return response.Response(serializer.data)
        data = self.get_object(token_list)
        return JsonResponse(data, safe=False)
            
class ProfileAPIView(views.APIView):
    def get_object(self, token_list):
        try:
            # token = self.request.get('iwana_user_token')
            token = '.'.join(token_list)
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            return User.objects.get(id=payload['user_id'])

        except jwt.ExpiredSignatureError as e:
            return response.Response({'error': 'Activations link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            return response.Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        head = request.GET.get("head")
        pay = request.GET.get("pay")
        signature = request.GET.get("signature")
        token_list = [head, pay, signature]
        
        user = self.get_object(token_list)
        serializer = ProfileSerializer(user)
        return response.Response(serializer.data)

def refresh_token(request):
    if request.method == "POST":
        data = (request.data)
        print(data)
        r = requests.post(
            '{0}://{1}/api/user/refresh/'.format(self.request.scheme, self.request.get_host()),
            json.dumps({
                "refresh": data['refresh'],
            }),
            headers={
                'Content-Type': 'application/json',
            },
        )
        res = r.json()
        print(res)
        return res

class ProfileDetailView(views.APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=int(pk))
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        user = self.get_object(pk=pk)
        print(user)
        serializer = ProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
