from django.shortcuts import get_object_or_404, redirect, render, reverse

from order.models import Order
from .services import StripePayment


def payment_process(request):
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        success_url = request.build_absolute_url(reverse("payment:completed"))
        cancel_url = request.build_absolute_url(reverse("payment:cancelled"))

        session = StripePayment(order, success_url, cancel_url)

        return redirect(session.url, code=303)

    else:
        return render("payment/process.html", locals())


def payment_completed(request):
    return render(request, "payment/completed.html")


def payment_canceled(request):
    return render(request, "payment/canceled.html")
