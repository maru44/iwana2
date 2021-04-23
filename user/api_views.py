from user.models import User
from rest_framework import views, status, response
from .serializers import UserSerializer, ProfileSerializer
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponseRedirect

# auth
from django.core.signing import BadSignature, SignatureExpired, loads, dumps

import jwt
import requests

from django.core import serializers
from django.template.loader import get_template

from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt import exceptions as jwt_exp

# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator


class UserInformationAPIView(views.APIView):
    def get_id(self, token_list):
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

        data = {"uid": self.get_id(token_list)}
        return JsonResponse(data, safe=False)


# login処理
class UserAPIView(views.APIView):
    def get_object(self, token_list):

        try:
            payload = jwt.decode(
                jwt=token_list, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            return User.objects.get(id=payload["user_id"])

        except jwt.ExpiredSignatureError:
            return "Activations link expired"
        except jwt.exceptions.DecodeError:
            return "Invalid Token"
        except User.DoesNotExist:
            return "user does not exists"

    def get(self, request, format=None):
        IWT = request.COOKIES.get("iwana_user_token")
        print(IWT)
        if not IWT:
            return response.Response(
                {"error": "No token"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = self.get_object(IWT)
        # if user.get("error") is not None:

        print(type(user))
        if type(user) == str:
            return response.Response(
                {"error": user}, status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            serializer = UserSerializer(user)
            return response.Response(serializer.data)
        return response.Response(
            {"error": "user is not activate"}, status=status.HTTP_400_BAD_REQUEST
        )

    # change is_active false
    def put(self, request, format=None):
        IWT = self.request.COOKEIS.get("iwana_user_token")
        user = self.get_object(IWT)
        if user.is_active:
            user.is_active = False
            user.save()
            return JsonResponse({"status": 200}, safe=False)
        return None


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
    # @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        data = self.request.data
        if User.objects.filter(email=data["email"], is_active=False).exists():
            User.objects.filter(email=data["email"], is_active=False).delete()
        if User.objects.filter(username=data["username"], is_active=False).exists():
            User.objects.filter(username=data["username"], is_active=False).delete()
        serializer = UserSerializer(data=data)
        password = data["password"]

        if serializer.is_valid():
            user = serializer.create(password, serializer.data)
            """
            r = requests.post(
                "{}/api/user/login/".format(settings.BACKEND_URL),
                {"username": user.username, "password": password},
            )
            res = r.json()
            """
            user.is_active = True
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
            # return JsonResponse(res, safe=False)
            return JsonResponse({"status": 200}, safe=False)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # change is_activate
    def put(self, request, format=None):
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

                return JsonResponse(
                    {"status": 200, "message": "success", "username": user.username},
                    safe=False,
                )

    return JsonResponse({"status": 400, "message": "Invalid token"}, safe=False)


class TokenObtainPair(jwt_views.TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except jwt_exp.TokenError as e:
            raise jwt_exp.InvalidToken(e.args[0])

        res = response.Response(serializer.validated_data, status=status.HTTP_200_OK)
        try:
            res.delete_cookie("iwana_user_token")
        except Exception as e:
            print(e)
            pass
        res.set_cookie(
            "iwana_user_token",
            serializer.validated_data["access"],
            max_age=60 * 60 * 24,
            httponly=True,
        )
        res.set_cookie(
            "iwana_refresh",
            serializer.validated_data["refresh"],
            max_age=60 * 60 * 24 * 30,
            httponly=True,
        )
        return res


class TokenRefresh(jwt_views.TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            res = response.Response(
                serializer.validated_data, status=status.HTTP_200_OK
            )
        except jwt_exp.TokenError as e:
            raise jwt_exp.InvalidToken(e.args[0])

        return res


def refresh_get(request):
    try:
        IRT = request.COOKIES["iwana_refresh"]
    except Exception as e:
        print(e)
    r = requests.post(
        f"{settings.BACKEND_URL}/api/user/refresh/token/",
        {
            "refresh": IRT,
        },
    )
    ret = r.json()
    res = JsonResponse({"status": 200}, safe=False)
    res.delete_cookie("iwana_user_token")
    res.set_cookie(
        "iwana_user_token",
        ret["access"],
        max_age=60 * 24 * 24 * 30,
        httponly=True,
    )
    return res


def delete_jwt(request):
    # print(request.COOKIES.get("iwana_user_token"))
    response = HttpResponseRedirect(f"{settings.FRONT_URL}")
    try:
        response.delete_cookie("iwana_user_token")
        response.delete_cookie("iwana_refresh")
    except Exception as e:
        print(e)
    return response
