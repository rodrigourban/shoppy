from django.apps import AppConfig

from django.db.models.signals import pre_save


class OrderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "order"

    def ready(self) -> None:
        from . import signals

        pre_save.connect(signals.activate_can_review_on_order_shipped)
        return super().ready()
