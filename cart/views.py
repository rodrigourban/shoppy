from pipes import Template
from typing import List
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib import messages

from .cart import Cart
from products.models import Product
# from coupons.forms import CouponApplyForm


class CartListView(TemplateView):
  template_name = 'cart/list.html'
  

def list(request):
  # coupon_form = CouponApplyForm()
  return render(
    request,
    'cart/list.html',
    # {'coupon_apply_form': coupon_form}
  )

@login_required
def checkout(request):
  pub_key = settings.STRIPE_API_KEY_PUBLISHABLE
  return render(
    request,
    'cart/checkout.html',
    {'pub_key': pub_key}
  )

def add(request, product_id):
  cart = Cart(request)
  cart.add(product_id)

  return render(
    request,
    'cart/partials/_menu_cart.html'
  )

def update_cart(request, product_id, action):
  cart = Cart(request)

  if action == 'increment':
    cart.add(product_id, 1, True)
  elif action == 'decrement':
    cart.add(product_id, -1, True)

  product = get_object_or_404(Product, pk=product_id)
  quantity = cart.get_product(product_id)['quantity']

  new_product = {
    'properties': {
      'id': product.id,
      'name': product.name,
      'image': product.get_image_url(),
      'slug': product.slug,
      'get_thumbnail': product.get_thumbnail(),
      'price': product.price,
    },
    'total_price': (product.price * quantity),
    'quantity': quantity
  }

  response = render(
    request,
    'cart/partials/_product.html',
    {
      'product': new_product
    }
  )

  response['HX-Trigger'] = 'update-menu-cart'

  return response

def success(request):
  return render(request, 'cart/success.html')

def hx_menu_cart(request):
  return render(
    request,
    'cart/partials/_menu_cart.html'
  )

def hx_total_cost(request):
  return render(
    request,
    'cart/partials/_total_cost.html'
  )