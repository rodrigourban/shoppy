from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.utils import timezone
from django.urls import reverse

from .forms import CouponApplyForm
from .models import Coupon

class CouponApplyView(CreateView):
  form_class = CouponApplyForm()

  def get_success_url(self):
    return reverse('cart:list')

  def form_valid(self, form):  
    now = timezone.now()
    code = form.cleaned_data['code']
    try:
      coupon = Coupon.objects.get(
        code__iexact=code,
        valid_from__lte=now,
        valid_to__gte=now
      )
      self.request.session['coupon_id'] = coupon.id
    except:
      self.request.session['coupon_id'] = None

    return super().form_valid(form)

