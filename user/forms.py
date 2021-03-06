from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm,PasswordResetForm,
    SetPasswordForm
)
from .models import User

class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password1']

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        User.objects.filter(username=username, is_active=False).delete()
        return username

class UserUpdateForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['name', 'intro']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['picture']

class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MySetPasswordForm(SetPasswordForm):
    """パスワード再設定用フォーム(パスワード忘れて再設定)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


