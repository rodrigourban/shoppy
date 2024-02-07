from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Order
from products.models import CanReview


@receiver(pre_save, sender=Order, dispatch_uid="order_shipped_can_review")
def activate_can_review_on_order_shipped(sender, instance, **kwargs):
    # only do it on save, when updated fields contains status change
    # i guess it would go something like this
    update_fields = kwargs.get("update_fields", {})
    if update_fields and "status" in update_fields:
        # order has a list of order items, create one instance of CanReview
        # for each
        user = instance.user
        for order_item in instance.order_items.all():
            product = order_item.product
            try:
                CanReview.objects.get(product__id=product.id)
            except CanReview.DoesNotExist:
                CanReview.objects.create(product=product, user=user)
