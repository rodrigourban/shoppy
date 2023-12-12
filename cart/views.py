from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView

from coupons.forms import CouponApplyForm
from products.models import Product

from .cart import Cart


class CartListView(TemplateView):
    template_name = "cart/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["coupon_apply_form"] = CouponApplyForm()
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "cart/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pub_key = settings.STRIPE_PUBLISHABLE_KEY
        context["pub_key"] = pub_key
        return context


class CartAddView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        cart.add(product_id)

        return render(request, "cart/partials/_menu_cart.html")


class CartUpdateView(View):
    def get(self, request, product_id, action):
        cart = Cart(request)

        if action == "increment":
            cart.add(product_id, 1, True)
        elif action == "decrement":
            cart.add(product_id, -1, True)
        elif action == "delete":
            cart.remove(product_id)
            response = render(request, "cart/partials/_product.html", {})
            response["HX-Trigger"] = "update-menu-cart"
            return response

        product = get_object_or_404(Product, pk=product_id)
        quantity = cart.get_product(product_id)["quantity"]

        new_product = {
            "properties": {
                "id": product.id,
                "name": product.name,
                "image": product.get_image_url(),
                "slug": product.slug,
                "get_thumbnail": product.get_thumbnail(),
                "price": product.price,
            },
            "total_price": (product.price * quantity),
            "quantity": quantity,
        }

        response = render(
            request, "cart/partials/_product.html", {"product": new_product}
        )

        response["HX-Trigger"] = "update-menu-cart"

        return response


class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = "cart/success.html"


class HxMenuCart(TemplateView):
    template_name = "cart/partials/_menu_cart.html"


class HxTotalPrice(TemplateView):
    template_name = "cart/partials/_total_price.html"
