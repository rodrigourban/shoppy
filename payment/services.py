from decimal import Decimal
from django.conf import settings

import stripe


class StripePayment:
    def create_session(items_in_cart):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=items_in_cart,
            mode="payment",
            success_url="http://localhost:8000/cart/success/",
            cancel_url="http://localhost:8000/cart/",
        )
        return session

    def checkout(order, success_url, cancel_url):
        stripe.api_key = settings.STRIPE_PUBLISHABLE_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        session_data = {
            "mode": "payment",
            "client_referece_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }

        for order_item in order.items.all():
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(order_item.price * Decimal("100")),
                        "currency": "usd",
                        "product_data": {"name": order_item.product.name},
                    },
                    "quantity": order_item.quantity,
                }
            )

        return stripe.checkout.Session.create(**session_data)
