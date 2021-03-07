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

class OfferingAPI(views.APIView):
    def get_object(self, wanted_slug):
        try:
            return Wanted.objects.get(slug=wanted_slug)
        except Wanted.DoesNotExist:
            raise Http404

    # gotten change
    def get(self, request, wanted_slug, format=None):
        wanted = self.get_object(wanted_slug)
        user = self.request.user
        data = {}
        if wanted.is_gotten == True:
            #wanted.update(is_gotten=False)
            wanted.is_gotten = False
            wanted.save()
            data = {
                "is_": 0,
            }
        else:
            #Wanted.objects.select_related
            wanted.is_gotten = True
            wanted.save()
            data = {
                "is_": 1,
            }
        return response.Response(data)
    
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

"""
#AWS
def scrape_api(request):
    scrape_url = settings.SQRAPE_URL_AWS
    if request.method == "POST":
        data = json.loads(request.body)
        keyword = data["keyword"]
        r = requests.post(
            scrape_url,
            json.dumps({
                "OperationType": "SCRAPE",
                "Keys": {
                    "keyword": keyword
                }
            }),
            headers={'Content-Type': 'application/json'},
        )
        datas = r.json()
        return JsonResponse(datas, safe=False)
"""

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
            headers={'Content-Type': 'application/json'},
        )
        datas = r.json()
        return JsonResponse(datas, safe=False)