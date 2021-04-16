from django.shortcuts import render, get_object_or_404, redirect
from .models import Wanted, Offer, Plat
from .forms import WantedForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import Http404

from django.contrib import messages

# to gen id
import random
import string

# to contact inquiry api
import requests
import json

from django.conf import settings

# integrity error (same sluug)
from django.db import IntegrityError


def gen_id():
    random_ = [
        random.choice(string.ascii_letters + string.digits + "-" + "_")
        for i in range(8)
    ]
    id_ = "".join(random_)
    return id_


def home(request):
    posts = (
        Wanted.objects.prefetch_related("plat")
        .select_related("user")
        .order_by("-posted")
    )
    context = {
        "posts": posts,
    }
    return render(request, "blog/home.html", context)


# detail of wanted
def det_wanted(request, slug):
    post = get_object_or_404(
        Wanted.objects.prefetch_related("plat").select_related("user"), slug=slug
    )
    # post = Wanted.objects.prefetch_related('plat').select_related('user').get(slug=slug)
    offers = (
        Offer.objects.select_related("wanted")
        .select_related("user")
        .filter(wanted=post)
        .order_by("-posted")
    )
    context = {
        "post": post,
        "offers": offers,
        "now": timezone.now(),
    }
    return render(request, "blog/detail.html", context)


# create wanted
@login_required
def create_wanted(request):
    plats = Plat.objects.all()
    if request.method == "POST":
        form = WantedForm(request.POST, request.FILES)
        # form = WantedForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user

            selected = request.POST.getlist("wanted_plat")  # platform many
            plats = Plat.objects.filter(name__in=selected)

            try:
                post.slug = gen_id()
                post.save()
            except IntegrityError:
                post.slug = gen_id()
                post.save()
            except Exception as e:
                print(e)

            post.plat.set(plats)
            messages.success(request, f"{post}を作成しました。")
            return redirect("home")
    else:
        form = WantedForm()
    context = {
        "form": form,
        "plats": plats,
        "func": "欲しいものを投稿する",
    }
    return render(request, "blog/post.html", context)


# update wanted
@login_required
def update_wanted(request, slug):
    wanted = get_object_or_404(
        Wanted.objects.prefetch_related("plat").select_related("user"), slug=slug
    )
    plats = Plat.objects.all()

    init_plats = []  # initial plat forms
    for plat in wanted.plat.all():
        init_plats.append(plat.name)

    if wanted.user == request.user:
        if request.method == "POST":
            form = WantedForm(
                request.POST, request.FILES, instance=wanted
            )  # instance is wanted
            # form = WantedForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)

                selected = request.POST.getlist("wanted_plat")  # platform many
                plats = Plat.objects.filter(name__in=selected)

                post.save()
                post.plat.set(plats)
                messages.success(request, f"{post}を更新しました。")
                return redirect("home")
        else:
            form = WantedForm(instance=wanted)  # instance is wantedf
        context = {
            "form": form,
            "plats": plats,
            "func": f'"{wanted}" を編集する',
            "init_plats": init_plats,  # this is initial plat forms
        }
        return render(request, "blog/post.html", context)
    else:
        raise Http404("This wanted does not yours.")


# delete wanted
@login_required
def delete_wanted(request, slug):
    wanted = get_object_or_404(
        Wanted.objects.prefetch_related("plat").select_related(), slug=slug
    )

    if wanted.user == request.user:
        messages.success(request, f"{wanted}を削除しました。")
        wanted.delete()
        return redirect("home")
    else:
        raise Http404("This wanted does not yours.")


def users_wanted(request, username):
    # target = User.objects.select_related().get(username=username)
    target = get_object_or_404(User.objects.select_related(), username=username)
    wanted = (
        Wanted.objects.prefetch_related("plat")
        .select_related("user")
        .filter(user=target)
        .order_by("-posted")
    )
    context = {
        "target": target,
        "posts": wanted,
    }
    return render(request, "blog/users_wanted.html", context)


def inq(request):
    inquiryUrl = settings.INQ_URL_AWS
    r = requests.post(
        inquiryUrl,
        json.dumps({"OperationType": "SCAN"}),
        headers={"Content-Type": "application/json"},
    )
    context = {
        "data": r.json()["Items"],
    }
    return render(request, "blog/inq.html", context)


def inquiry(request):
    inquiryUrl = settings.INQ_URL_AWS
    if request.method == "POST":
        name = request.POST.get("inq_name")
        content = request.POST.get("inq_content")
        cat = request.POST.get("inq_category")
        mail = request.POST.get("inq_mail")
        data = {"name": name, "mail": mail, "category": cat, "content": content}
        r = requests.post(
            inquiryUrl,
            json.dumps({"OperationType": "PUT", "Keys": data}),
            headers={"Content-Type": "application/json"},
        )
        if r.status_code != 200:
            # if r.json()["ResponseMetadata"]["HTTPStatusCode"] != 200:
            # if r != 200:
            messages.error(request, "お問い合わせに失敗しました。")
            return redirect("inquiry")
        else:
            messages.success(request, "お問い合わせを承りました。")
            return redirect("home")
    return render(request, "blog/inquiry.html")


def global_search(request):
    return render(request, "blog/global_search.html")
