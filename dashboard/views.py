from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView

from products.models import Product, Favorite
from accounts.forms import UserProfileForm, ShippingInformationForm


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(created_by=self.request.user)
        return context


class FavoritesView(LoginRequiredMixin, ListView):
    template_name = "dashboard/favorite_list.html"
    context_object_name = "favorite_list"
    model = Favorite

    def get_queryset(self):
        return Favorite.objects.filter(created_by=self.request.user.pk)


class CustomerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customer_profile.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["profile_form"] = UserProfileForm
        context["shipping_form"] = ShippingInformationForm
        return context


class CustomerOrdersView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customer_orders.html"
