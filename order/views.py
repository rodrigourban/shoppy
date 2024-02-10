import json

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

from payment.services import StripePayment
from accounts.models import ShippingInfo

from .models import Order, OrderItem


class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        shipping_info = json.loads(request.body)
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
        session = StripePayment.create_session(items_in_cart)
        payment_intent = session.payment_intent

        if "id" in shipping_info.keys():
            shipping_obj = ShippingInfo.objects.get(id=shipping_info["id"])
            shipping_info["first_name"] = shipping_obj.first_name
            shipping_info["last_name"] = shipping_obj.last_name
            shipping_info["address"] = shipping_obj.address
            shipping_info["city"] = shipping_obj.city
            shipping_info["zipcode"] = shipping_obj.zipcode
            shipping_info["phone"] = shipping_obj.phone
            shipping_info["email"] = shipping_obj.email

        order = Order.objects.create(
            user=request.user,
            first_name=shipping_info["first_name"],
            last_name=shipping_info["last_name"],
            email=shipping_info["email"],
            address=shipping_info["address"],
            zipcode=shipping_info["zipcode"],
            city=shipping_info["city"],
            phone=shipping_info["phone"],
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
            # reduce stock
            new_quantity = product.stock - quantity
            if new_quantity > 0:
                product.stock = new_quantity
                product.save()
            else:
                product.stock = 0
                product.available = False
                product.save()
                # [OUT OF MVP SCOPE] send an email to admins letting them know
                # this item is out of stock
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


"""
    Right now all order status changing look the same,
    and we could be tempted to generate a general method
    but in the future each action is going to do different
    things, so it's better to have them as different
    functions.
"""


@staff_member_required
def admin_order_ship(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "shipped"
    order.save(update_fields=["status"])
    return redirect("admin:order_order_changelist")


@staff_member_required
def admin_order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # return product stock
    for item in order.order_items.all():
        item.product.stock += item.quantity
        if not item.product.available:
            item.product.available = True
        item.product.save()

    # [OUT OF SCOPE OF MVP] return money to customer

    order.status = "cancelled"
    order.save(update_fields=["status"])
    return redirect("admin:order_order_changelist")


@staff_member_required
def admin_order_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "completed"
    order.save(update_fields=["status"])
    return redirect("admin:order_order_changelist")
