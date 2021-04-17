from user.models import User
from rest_framework import views, status, response
from .serializers import UserSerializer, ProfileSerializer
from django.conf import settings
from django.http import JsonResponse, Http404

# auth
from django.core.signing import BadSignature, SignatureExpired, loads, dumps

import jwt
import json
import requests

from django.core import serializers
from django.template.loader import get_template

from django.views.generic.base import csrf_exempt
from django.utils.decorators import method_decorator


class UserInformationAPIView(views.APIView):
    def get_object(self, token_list):
        try:
            token = ".".join(token_list)
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            return payload["user_id"]
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Expired access token"}, safe=False)
        except jwt.exceptions.DecodeError:
            return response.Response(
                serializers.serialize("json", {"error": "Invalid Token"}),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request, format=None):
        head = request.GET.get("head")
        pay = request.GET.get("pay")
        signature = request.GET.get("signature")
        token_list = [head, pay, signature]

        data = {"uid": self.get_object(token_list)}
        return JsonResponse(data, safe=False)


# login処理
class UserAPIView(views.APIView):
    def get_object(self, token_list):
        try:
            token = ".".join(token_list)
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            return User.objects.get(id=payload["user_id"])

        except jwt.ExpiredSignatureError:
            return response.Response(
                {"error": "Activations link expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError:
            return response.Response(
                {"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return response.Response({"error": "user does not exists"})

    def get(self, request, format=None):
        head = request.GET.get("head")
        pay = request.GET.get("pay")
        signature = request.GET.get("signature")
        token_list = [head, pay, signature]

        user = self.get_object(token_list)
        if user.is_active:
            serializer = UserSerializer(user)
            return response.Response(serializer.data)
        return None


def refresh_token(request):
    if request.method == "POST":
        data = request.data
        r = requests.post(
            "{0}://{1}/api/user/refresh/".format(request.scheme, request.get_host()),
            json.dumps(
                {
                    "refresh": data["refresh"],
                }
            ),
            headers={
                "Content-Type": "application/json",
            },
        )
        res = r.json()
        return res


class ProfileDetailView(views.APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=int(pk))
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        user = self.get_object(pk=pk)
        serializer = ProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateAPIView(views.APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        data = self.request.data
        if User.objects.filter(email=data["email"], is_active=False).exists():
            User.objects.filter(email=data["email"], is_active=False).delete()
        if User.objects.filter(username=data["username"], is_active=False).exists():
            User.objects.filter(email=data["username"], is_active=False).delete()
        serializer = UserSerializer(data=data)
        password = data["password"]

        if serializer.is_valid():
            user = serializer.create(password, serializer.data)
            r = requests.post(
                "{}/api/user/login/".format(settings.BACKEND_URL),
                {"username": user.username, "password": password},
            )
            res = r.json()
            user.is_active = False
            user.save()

            context = {
                "protocol": self.request.scheme,
                "domain": settings.FRONT_DOMAIN,
                "token": dumps(user.pk),
                "user": user,
            }
            from_email = settings.EMAIL_HOST_USER
            subject_template = get_template("user/mail_template/create/subject.txt")
            subject = subject_template.render(context)
            message_template = get_template("user/mail_template/create/message.txt")
            message = message_template.render(context)
            user.email_user(subject, message, from_email)
            # return JsonResponse({'status': 200}, safe=False)
            return JsonResponse(res, safe=False)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        pass


def user_complete_api(request, token):
    timeout_seconds = getattr(settings, "ACTIVATION_TIMEOUT_SECONDS", 60 * 60 * 24)
    try:
        user_pk = loads(token, max_age=timeout_seconds)
    # 期限切れ
    except SignatureExpired:
        return JsonResponse({"status": 400, "message": "Token expired"}, safe=False)
    # tokenが間違っている
    except BadSignature:
        return JsonResponse({"status": 400, "message": "Invalid token"}, safe=False)

    else:
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return JsonResponse({"status": 400, "message": "Invalid token"}, safe=False)
        else:
            if not user.is_active:
                # 問題なければ本登録とする
                user.is_active = True
                user.save()

                # password が取れないから無理
                return JsonResponse(
                    {"status": 200, "message": "success", "username": user.username},
                    safe=False,
                )

    return JsonResponse({"status": 400, "message": "Invalid token"}, safe=False)
