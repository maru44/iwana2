from django.contrib import admin
from .models import Plat, Offer, Wanted

admin.site.register(Wanted)
admin.site.register(Offer)
admin.site.register(Plat)