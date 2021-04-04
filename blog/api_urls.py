from django.urls import path
from . import api_views as api

app_name = 'api'
urlpatterns = [
    # wanted list post 
    path('wanted/', api.WantedAPI.as_view(), name="wanted_api"),
    # wanted detail update delete
    path('wanted/<wanted_slug>/', api.WantedDetailAPI.as_view(), name="wanted_detail_api"),
    # user wanted list post
    path('wanted/u/<username>/', api.WantedUsersAPI.as_view()),
    # offer or change wanted offer
    path('offering/<wanted_slug>/', api.OfferingAPI.as_view(), name='offering'),
    # scraping
    path('scrape/', api.scrape_api, name="scrape"),
    path('batch/<wanted_slug>/', api.batch_offer, name='offer_batch'),
    # give csrftoken
    path('csrf/', api.csrf, name="csrf"),
]