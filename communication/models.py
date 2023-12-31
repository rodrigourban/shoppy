from django.contrib.auth import get_user_model
from django.db import models

from products.models import Product


class Conversation(models.Model):
    product = models.ForeignKey(
        Product, related_name="conversations", on_delete=models.CASCADE
    )
    members = models.ManyToManyField(get_user_model(), related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-modified_at",)

    @property
    def latest_message(self):
        return Message.objects.filter(conversation=self.pk).last()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(),
        related_name="created_messages",
        on_delete=models.CASCADE,
    )
