from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import ShippingInfo


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "username")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "username")


class ShippingInformationForm(forms.ModelForm):
    class Meta:
        model = ShippingInfo
        fields = ("address", "zipcode", "city", "phone")
