from django.urls import path

from .views import CustomerProfileView, DashboardView, FavoritesView, CustomerOrdersView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="index"),
    path("profile/", CustomerProfileView.as_view(), name="customer_profile"),
    path("orders/", CustomerOrdersView.as_view(), name="customer_orders"),
    path("favorites/", FavoritesView.as_view(), name="favorites"),
]
