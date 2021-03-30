from django.shortcuts import get_object_or_404
from .models import *
from user.models import User
from rest_framework import views, status, permissions, response
from .serializers import *

from django.conf import settings
import requests, json
from django.contrib import messages
from django.http import JsonResponse, Http404

# for notify mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template

# for batch of offer
from django.utils import timezone

# csrf
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

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

        PAGI_NUM = 2

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
        serializer = WantedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        wanted = self.get_object(wanted_slug)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, wanted_slug, format=None):
        wanted = self.get_object(wanted_slug)
        wanted.delete()
        return response.Response(status=staus.HTTP_204_NO_CONTENT)

def gotten_change(request, wanted_slug):
    wanted = get_object_or_404(wanted, slug=wanted_slug)
    if request.method == "GET":
        user = self.request.user
        data = {}
        if wanted.is_gotten:
            wanted.update(is_gotten=False)
            data = {
                "is_": 0,
            }
        else:
            wanted.update(is_gotten=True)
            data = {
                "is_": 1,
            }
        return JsonResponse(data, safe=False)

class OfferingAPI(views.APIView):
    def get_object(self, wanted_slug):
        try:
            return Wanted.objects.get(slug=wanted_slug)
        except Wanted.DoesNotExist:
            raise Http404

    # offer list
    def get(self, request, wanted_slug, formta=None):
        wanted = self.get_object(wanted_slug)
        offers = Offer.objects.select_related('user').select_related('wanted')\
            .filter(wanted=wanted).order_by('posted')
        serializer = OfferSerializer(offers, many=True)
        return response.Response(serializer.data)
    
    
    # offer post
    def post(self, request, wanted_slug, format=None):
        wanted = self.get_object(wanted_slug)
        user = self.request.user
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            if user.is_authenticated:
                serializer.save(wanted=wanted, user=user)
                offer_user = user

                # send notify with email rapidly
                if not user.is_superuser:
                    offer_mail(self.request, wanted, offer_user)
                else:
                    #offer_mail_batch(self.request, wanted, offer_user)
                    pass

            else:
                serializer.save(wanted=wanted)
                offer_user = "アノニマスユーザー"


            return response.Response(serializer.data)
        return response.Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

# heroku scrape
# @csrf_exempt # for test
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

def csrf(request):
    permission_classes = [permissions.AllowAny, ]

    token = get_token(request)
    data = {
        "token": token,
    }
    return JsonResponse(data, safe=False)