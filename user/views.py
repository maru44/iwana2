from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest
from django.utils.encoding import force_bytes, force_text
from django.views import generic
from django.template.loader import get_template
from django.contrib.auth.views import (
        LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordChangeView, PasswordChangeDoneView,
        PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from .forms import (
    UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
)
from django.urls import reverse_lazy
from .models import User

class UserCreate(generic.CreateView):
    template_name = 'user/register.html'
    form_class = UserRegisterForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        #from_email = settings.EMAIL_HOST_USER
        from_email = settings.FROM_EMAIL

        subject_template = get_template('user/mail_template/create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('user/mail_template/create/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message, from_email)

        return redirect('user:register_done')

class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'user/user_create_done.html'

def user_create_complete(request, token):
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)
    try:
        user_pk = loads(token, max_age=timeout_seconds)
    
    # 期限切れ
    except SignatureExpired:
        return HttpResponseBadRequest()

    # tokenが間違っている
    except BadSignature:
        return HttpResponseBadRequest()

    else:
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            if not user.is_active:
                # 問題なければ本登録とする
                user.is_active = True
                user.save()

                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'{user}様 Iwanaにようこそ')
                return redirect('home')

    return HttpResponseBadRequest()

class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'user/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)
    
    def get(self, request, **kwargs):
        token = kwargs.get('token')
 
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()

                    auth_login(request, user)
                    
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

@login_required
def profile(request):
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "プロフィールを変更しました。")
            return redirect('home')
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user)

    return render(request, 'user/profile.html', {'uform': uform, 'pform': pform})

class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'user/mail_template/password_reset/subject.txt'
    email_template_name = 'user/mail_template/password_reset/message.txt'
    template_name = 'user/password_reset.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('user:reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'user/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('user:reset_complete')
    template_name = 'user/password_reset_confirm.html'

class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'user/password_reset_complete.html'

class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('user:change_done')
    template_name = 'user/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'user/password_change_done.html'

def detail(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'user': user,
    }
    return render(request, 'user/user_detail.html', context)

@login_required
def delete(request, username):
    user = get_object_or_404(User, username=username)
    #user = request.user
    User.objects.filter(username=user.username).delete()
    return redirect('home')

@login_required
def delete_conf(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'user/user_delete.html')