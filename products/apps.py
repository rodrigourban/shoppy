from django.apps import AppConfig
from django.db.models.signals import post_save


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"

    def ready(self) -> None:
        from . import signals

        post_save.connect(signals.deactivate_user_can_review)

        return super().ready()
