from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Review, CanReview


@receiver(post_save, sender=Review, dispatch_uid="deactivate_user_can_review")
def deactivate_user_can_review(sender, instance, created, **kwargs):

    if created and isinstance(instance, Review):
        # find the CanReview for this object, and delete it
        try:
            product = instance.product
            can_review_obj = CanReview.objects.get(product__id=product.id)
            can_review_obj.delete()
        except CanReview.DoesNotExist:
            print("Signal: Can review does not exist.")
