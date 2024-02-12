from django.urls import path

from .views import (
    CustomerProfileView,
    DashboardView,
    FavoritesView,
    CustomerOrdersView,
    CustomerOrderDetailView,
    CustomerShippingInfoCreateForm,
    ShippingInfoViewset,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="index"),
    path("profile/", CustomerProfileView.as_view(), name="customer_profile"),
    path("orders/", CustomerOrdersView.as_view(), name="customer_orders"),
    path(
        "orders/<int:order_id>/",
        CustomerOrderDetailView.as_view(),
        name="customer_order_detail",
    ),
    path(
        "profile/create-shipping-info-form/",
        CustomerShippingInfoCreateForm.as_view(),
        name="add_shipping_form",
    ),
    path(
        "profile/customer-shipping-info/",
        ShippingInfoViewset.as_view(),
        name="get_create_shipping_info",
    ),
    path(
        "profile/delete-shipping-info/<int:shipping_id>",
        ShippingInfoViewset.as_view(),
        name="delete_shipping_info",
    ),
    path("favorites/", FavoritesView.as_view(), name="favorites"),
]
