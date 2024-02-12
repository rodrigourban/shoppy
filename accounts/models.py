from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    pass


class ShippingInfo(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    # This is just a straight forward solution
    # but it only supports USA phone format
    # in a real world scenario, this should be changed
    # to use a more flexible solution that encompass all
    # possible phone formats.
    phone_regex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phone = models.CharField(
        max_length=16, unique=True, validators=[phone_regex]
    )
    email = models.EmailField(max_length=254)
    user = models.ForeignKey(
        CustomUser, related_name="shipping", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
