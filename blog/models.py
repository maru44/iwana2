from django.db import models
from django.utils.translation import ugettext_lazy as _
from user.models import User
from django.core.mail import send_mail


# table of platform
class Plat(models.Model):
    slug = models.CharField(_("Slug"), max_length=24)
    name = models.CharField(_("名前"), max_length=24)
    host = models.CharField(_("ドメイン"), max_length=48, blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    slug = models.CharField(_("slug"), max_length=24)
    name = models.CharField(_("名前"), max_length=24)


# table of want
class Wanted(models.Model):
    slug = models.SlugField(
        _("slug"), max_length=16, unique=True, blank=True, null=True
    )
    want_name = models.CharField(_("欲しいもの"), max_length=36)
    posted = models.DateTimeField(_("投稿日"), auto_now_add=True)
    picture = models.ImageField(_("画像"), upload_to="wanted/", default="default.png")
    is_gotten = models.BooleanField(_("取得済み"), default=False)
    want_intro = models.TextField(_("説明"), max_length=800, blank=True, null=True)
    want_price = models.IntegerField(_("値段"), blank=True, null=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    plat = models.ManyToManyField(Plat)

    is_accept_official = models.BooleanField(_("公式からのオファーを受け取りますか？"), default=True)

    def __str__(self):
        return self.want_name

    def offer_count(self):
        return Offer.objects.filter(wanted=self).count()

    def notify_mail(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.user.email], **kwargs)


# offer
class Offer(models.Model):
    offer_url = models.CharField(_("オファーurl"), max_length=100)
    posted = models.DateTimeField(_("投稿日"), auto_now_add=True)
    offer_mess = models.TextField(_("メッセージ"), max_length=400, blank=True, null=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    wanted = models.ForeignKey(Wanted, blank=True, null=True, on_delete=models.SET_NULL)

    is_by_official = models.BooleanField(_("公式からのオファー"), default=False)

    class HowGood(models.TextChoices):
        GOOD = "5", _("いい！")
        SOSO = "3", _("まあまあ")
        NO = "1", _("ちょっと違う")

    how_good = models.CharField(
        _("フィット感"), max_length=2, choices=HowGood.choices, blank=True, null=True
    )

    is_noticed = models.BooleanField(_("通知済み"), default=False)

    def __str__(self):
        if self.wanted:
            return "{0} @{1}".format(self.wanted, self.posted)
        else:
            return self.offer_url
