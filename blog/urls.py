from django.urls import path
from . import views
from . import api_views as api

urlpatterns = [
    path('', views.home, name="home"),
    # detail wanted
    path('wanted/<slug>/', views.det_wanted, name="detail"),
    # update wanted
    path('update/<slug>/', views.update_wanted, name="update"),
    # delete wanted
    path('delete/<slug>/', views.delete_wanted, name="delete"),
    # post wanted
    path('post/', views.create_wanted, name="post"),
    # wanted list per users
    path('wanteds/<username>/', views.users_wanted, name="users"),
    # inquiry list
    #path('inq/', views.inq, name="inq"),
    # inquiry post
    path('inquiry/', views.inquiry, name="inquiry"),
    #scrape mercari and rakuma
    path('global/', views.global_search, name="global_search"),
    #########################################
    #                                       #
    #                 API                   #
    #                                       #
    #########################################
    path('api/wanted/<wanted_slug>/', api.OfferingAPI.as_view(), name='offering'),
    path('api/scrape/', api.scrape_api, name="scrape"),
    path('api/batch/<wanted_slug>/', api.batch_offer, name='offer_batch'),
]