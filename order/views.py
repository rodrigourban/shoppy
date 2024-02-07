import json

import stripe
import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import View

from cart.cart import Cart
from celery import shared_task

from .models import Order, OrderItem


class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        data = json.loads(request.body)
        total_price = 0

        items_in_cart = []
        for item in cart:
            product = item["properties"]
            total_price += product.price * int(item["quantity"])

            items_in_cart.append(
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": product.name},
                        "unit_amount": int(
                            product.price * 100
                        ),  # Stripe only accepts integer (499 -> 4,99)
                    },
                    "quantity": item["quantity"],
                }
            )

        # create a service for this to handle multiple payment methods
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=items_in_cart,
            mode="payment",
            success_url="http://localhost:8000/cart/success/",
            cancel_url="http://localhost:8000/cart/",
        )
        payment_intent = session.payment_intent

        order = Order.objects.create(
            user=request.user,
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            address=data["address"],
            zipcode=data["zipcode"],
            city=data["city"],
            phone=data["phone"],
            paid=True,
            paid_amount=total_price,
        )

        if cart.coupon:
            order.coupon = cart.coupon
            order.discount = cart.coupon.discount

        order.payment_intent = payment_intent
        order.paid_amount = total_price
        order.paid = True
        order.save()

        for item in cart:
            product = item["properties"]
            quantity = int(item["quantity"])
            price = product.price * quantity

            item = OrderItem.objects.create(
                order=order, product=product, price=price, quantity=quantity
            )

        cart.clear()
        # send an async task for e-mail confirmation
        # order_created.delay(order.id)

        return JsonResponse({"session": session, "order": payment_intent})


@shared_task
def order_created(order_id):
    """
    Task to async send an email notification when an order
    was created successfully.
    """
    order = Order.objects.get(id=order_id)
    subject = f"Order number {order.id}"
    message = (
        f"Dear {order.first_name}, \n\n"
        f"You have succesfully placed an order."
        f"Your order ID is {order.id}"
    )
    mail_sent = send_mail(subject, message, "admin@shoppy.com", [order.email])

    return mail_sent


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/order/detail.html", {"order": order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string("order/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")],
    )

    return response


@staff_member_required
def admin_order_ship(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "SHIPPED"
    order.save(update_fields=["status"])
    return redirect("admin:order_order_changelist")
