from django.urls import path

from .views import (
    CartAddView,
    CartListView,
    CartUpdateView,
    CheckoutView,
    HxMenuCart,
    HxTotalPrice,
    SuccessView,
)

app_name = "cart"

urlpatterns = [
    path("", CartListView.as_view(), name="list"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("add/<int:product_id>/", CartAddView.as_view(), name="add"),
    path(
        "update_cart/<int:product_id>/<str:action>/",
        CartUpdateView.as_view(),
        name="update",
    ),
    path("hx_menu_cart/", HxMenuCart.as_view(), name="hx_menu_cart"),
    path("hx_total_price/", HxTotalPrice.as_view(), name="hx_total_price"),
    path("success/", SuccessView.as_view(), name="success"),
]
