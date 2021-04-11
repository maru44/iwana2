from django.shortcuts import get_object_or_404
from .models import *
from user.models import User
from rest_framework import views, status, permissions, response
from .serializers import *

from django.conf import settings
import requests, json
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse

# for notify mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template

# for batch of offer
from django.utils import timezone

# csrf
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

# for id
import random, string

# user from jwt
import jwt
from django.core import serializers

def gen_id():
    random_ = [random.choice(string.ascii_letters + string.digits + '-' + '_') for i in range(8)]
    id_ = ''.join(random_)
    return id_

def user_id_from_jwt(token):
    try:
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except Exception as e:
        # print(e, 'aaaa')
        return None
    """
    except jwt.ExpiredSignatureError as e:
        return response.Response(serializers.serialize("json", {'error': 'Activations link expired'}), status=status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as e:
        return response.Response(serializers.serialize("json", {'error': 'Invalid Token'}), status=status.HTTP_400_BAD_REQUEST)
    """

def offer_mail(req, obj, offer_user):
    current_site = get_current_site(req)
    domain = current_site.domain
    context = {
        "user": obj.user,
        'protocol': req.scheme,
        'domain': domain,
        'slug': obj.slug,
        'offeruser': offer_user,
        #'offer': offer_url,
    }
    from_email = settings.FROM_EMAIL
    subject_template = get_template('blog/mail_template/offer_notify/subject.txt')
    subject = subject_template.render(context)
    message_template = get_template('blog/mail_template/offer_notify/message.txt')
    message = message_template.render(context)
    obj.notify_mail(subject, message, from_email)

def batch_offer(request, wanted_slug):
    permission_classes = [permission.AllowAny, ]

    api_url = settings.AWS_BATCH_URL
    if request.method == "POST":
        data = json.loads(request.body)

        wanted = wanted_slug

        if request.user.is_authenticated:
            from_user = "Iwana公式"
        else:
            from_user = "非ログインユーザー"

        now = timezone.now()
        dt = strftime("%Y%m%d%H%M%s")
        
        r = requests.post(
            api_url,
            json.dumps({
                "wanted": wanted,
                "from_user": fron_user,
                "dt": dt,
            }),
            headers={'Content-Type': 'applications/json'},
        )

class WantedAPI(views.APIView):
    def get(self, request, format=None):

        PAGI_NUM = 5

        page = request.GET.get('page')
        
        if page is not None:
            int_page = int(page)
        else:
            int_page = 1

        wanteds = Wanted.objects.select_related('user')\
            .prefetch_related('plat').order_by('-posted')[
                ((int_page - 1) * PAGI_NUM):
                int_page * PAGI_NUM + 1
            ]
        
        serializer = WantedSerializer(wanteds, many=True)
        return response.Response(serializer.data)

    def post(self, request, format=None):
        req_data = request.data.copy()
        selected = []
        if req_data.get('plat[]'):
            selected = req_data.pop('plat[]')

        serializer = WantedSerializer(data=request.data)

        if serializer.is_valid():
            try:
                id_ = gen_id()
                serializer.save(slug=id_)
            except IntegrityError:
                id_ = gen_id()
                serializer.save(slug=id_)
            except Exception as e:
                print(e)

            plats = Plat.objects.filter(name__in=selected)
            print(plats)

            want = Wanted.objects.get(slug=id_)
            want.plat.set(plats)

            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# detail of wanted
class WantedDetailAPI(views.APIView):
    def get_object(self, wanted_slug):
        try:
            return Wanted.objects.get(slug=wanted_slug)
        except Wanted.DoesNotExist:
            raise Http404

    def get(self, request, wanted_slug, format=None):
        wanted = self.get_object(wanted_slug)
        serializer = WantedSerializer(wanted)
        return response.Response(serializer.data)

    def put(self, request, wanted_slug, format=None):
        IWT = self.request.COOKIES.get('iwana_user_token')
        user_id = user_id_from_jwt(IWT)
        
        wanted = self.get_object(wanted_slug)

        # platform
        req_data = request.data.copy()
        selected = []
        if req_data.get('plat[]'):
            selected = req_data.pop('plat[]')
        plats = Plat.objects.filter(name__in=selected)
        wanted.plat.set(plats)

        if wanted.user.pk == user_id:
            serializer = WantedSerializer(wanted, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(status=stauts.HTTP_403_FORBIDDEN)

    def delete(self, request, wanted_slug, format=None):
        IWT = self.request.COOKIES.get('iwana_user_token')
        user_id = user_id_from_jwt(IWT)
        wanted = self.get_object(wanted_slug)
        if wanted.user.pk == user_id:
            wanted.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=stauts.HTTP_403_FORBIDDEN)

# users wanted list
class WantedUsersAPI(views.APIView):
    def get_object(self, request, user):
        PAGI_NUM = 5

        page = request.GET.get('page')
        
        if page is not None:
            int_page = int(page)
        else:
            int_page = 1

        try:
            return Wanted.objects.select_related('user')\
                .prefetch_related('plat').filter(user=user)\
                .order_by('-posted')[
                    ((int_page - 1) * PAGI_NUM): int_page * PAGI_NUM + 1
                ]
        except Wanted.DoesNotExist:
            raise Http404

    def get_user(self, request, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
    
    def get(self, request, username, format=None):
        user = self.get_user(request, username)
        wanted = self.get_object(request, user)
        serializer = WantedSerializer(wanted, many=True)
        user_serializer = UserSerializer(user, many=False)
        return_data = {
            'wanteds': serializer.data,
            'user': user_serializer.data,
        }
        # return response.Response(serializer.data)
        return JsonResponse(return_data, safe=False)

# offering
class OfferingAPI(views.APIView):
    def get_object(self, wanted_slug):
        try:
            return Wanted.objects.get(slug=wanted_slug)
        except Wanted.DoesNotExist:
            raise Http404

    # offer list
    def get(self, request, wanted_slug, format=None):
        wanted = self.get_object(wanted_slug)
        offers = Offer.objects.select_related('user').select_related('wanted')\
            .filter(wanted=wanted).order_by('posted')
        serializer = OfferSerializer(offers, many=True)
        return response.Response(serializer.data)
    
    # offer post
    def post(self, request, wanted_slug, format=None):
        wanted = self.get_object(wanted_slug)
        # IWT = self.request.COOKIES.get('iwana_user_token') # for httpOnly
        # user_id = user_id_from_jwt(IWT)
        user_id = request.data.get('user')
        print(user_id)
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            if user_id is not None:
                user = User.objects.get(pk=user_id)
                serializer.save(wanted=wanted, user=user)
            else:
                serializer.save(wanted=wanted)

            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def test(request):
    if request.method == "POST":
        jwt_ = request.COOKIES.get('iwana_user_token')
        user_id = user_id_from_jwt(jwt_)
        return JsonResponse({"user": user_id}, safe=False)

# change is_gotten
def gotten_change(request, wanted_slug):
    wanted = get_object_or_404(Wanted, slug=wanted_slug)
    if request.method == "GET":
        data = {}
        if wanted.is_gotten:
            wanted.is_gotten = False
            wanted.save()
            data = {
                "is_": 0,
            }
        else:
            wanted.is_gotten = True
            wanted.save()
            data = {
                "is_": 1,
            }
        return JsonResponse(data, safe=False)


# heroku scrape
def scrape_api(request):
    permission_classes = [permissions.AllowAny, ]
    
    scrape_url = settings.SCRAPE_HEROKU
    if request.method == "POST":
        data = json.loads(request.body)
        keyword = data["keyword"]
        category = data["category"]
        sold = data["sold"]
        r = requests.post(
            scrape_url,
            json.dumps({
                "keyword": keyword,
                "narrowdown": {
                    "category": category,
                    "sold": sold,
                }
            }),
            headers={
                'Content-Type': 'application/json',
            },
        )
        datas = r.json()
        return JsonResponse(datas, safe=False)

    elif request.method == "GET":
        keyword = request.GET.get('keyword')
        category = request.GET.get('category')
        sold = request.GET.get('sold')
        r = requests.post(
            scrape_url,
            json.dumps({
                "keyword": keyword,
                "narrowdown": {
                    "category": category,
                    "sold": sold,
                }
            }),
            headers={
                'Content-Type': 'application/json',
            },
        )
        datas = r.json()
        return JsonResponse(datas, safe=False)

def csrf(request):
    permission_classes = [permissions.AllowAny, ]

    token = get_token(request)
    data = {
        "token": token,
    }
    return JsonResponse(data, safe=False)

def inquiry(request):
    inquiryUrl = settings.INQ_URL_AWS
    if request.method == "POST":
        bod = json.loads(request.body)
        data = {
            "name": bod['name'],
            "mail": bod['mail'],
            "category": bod['category'],
            "content": bod['content']
        }
        r = requests.post(
            inquiryUrl,
            json.dumps({
                "OperationType": "PUT",
                "Keys": data
            }),
            headers={'Content-Type': 'application/json'},
        )
        return JsonResponse({'status': r.status_code }, safe=False)
