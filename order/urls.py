from django.urls import path

from .views import (
    OrderCreateView,
    admin_order_detail,
    admin_order_pdf,
    admin_order_ship,
    admin_order_cancel,
    admin_order_completed,
)

app_name = "orders"

urlpatterns = [
    path("create/", OrderCreateView.as_view(), name="create"),
    path(
        "admin/order/<int:order_id>/",
        admin_order_detail,
        name="admin_order_detail",
    ),
    path(
        "admin/order/<int:order_id>/",
        admin_order_detail,
        name="admin_order_detail",
    ),
    path(
        "admin/order/<int:order_id>/pdf/",
        admin_order_pdf,
        name="admin_order_pdf",
    ),
    path(
        "admin/order/<int:order_id>/shipped",
        admin_order_ship,
        name="ship_order",
    ),
    path(
        "admin/order/<int:order_id>/cancelled",
        admin_order_cancel,
        name="cancel_order",
    ),
    path(
        "admin/order/<int:order_id>/completed",
        admin_order_completed,
        name="complete_order",
    ),
]
