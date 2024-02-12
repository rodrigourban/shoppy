from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView, ListView

from products.models import Product, Favorite
from accounts.forms import (
    ShippingInformationForm,
)
from order.models import Order, OrderItem
from accounts.models import ShippingInfo


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(
            created_by=self.request.user
        )
        return context


class FavoritesView(LoginRequiredMixin, ListView):
    template_name = "dashboard/favorite_list.html"
    context_object_name = "favorite_list"
    model = Favorite

    def get_queryset(self):
        return Favorite.objects.filter(created_by=self.request.user.pk)


class CustomerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customer_profile.html"


class ShippingInfoViewset(LoginRequiredMixin, View):
    def get(self, request, **kwargs) -> dict[str, Any]:
        shipping_info_list = ShippingInfo.objects.filter(
            user=self.request.user.pk
        )
        return render(
            request,
            "dashboard/partials/_shipping_info_list.html",
            {
                "shipping_info_list": shipping_info_list,
            },
        )

    def post(self, request, **kwargs):
        form = ShippingInformationForm(request.POST)
        if form.is_valid():
            shipping = form.save(commit=False)
            shipping.user = self.request.user
            shipping.save()

            return HttpResponse(headers={"HX-Trigger": "task-list-changed"})
        else:
            # handle errors
            return render(
                request,
                "dashboard/partials/_new_shipping_info_form.html",
                {"shipping_form": form},
            )

    def delete(self, request, shipping_id, **kwargs):
        # delete the element and trigger re-render of shipping list
        shipping_obj = get_object_or_404(ShippingInfo, pk=shipping_id)
        shipping_obj.delete()
        return HttpResponse(headers={"HX-Trigger": "task-list-changed"})


class CustomerShippingInfoCreateForm(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/partials/_new_shipping_info_form.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["shipping_form"] = ShippingInformationForm()
        return context


class CustomerOrdersView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customer_orders.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["order_list"] = Order.objects.filter(user=self.request.user.pk)
        return context


class CustomerOrderDetailView(LoginRequiredMixin, View):

    def get(self, request, order_id, **kwargs: Any) -> dict[str, Any]:
        # Only let order user or admin see this view
        try:
            order = OrderItem.objects.filter(
                order__id=order_id
            ).select_related("order", "product")
            if len(order) > 0 and (
                request.user.is_superuser
                or order[0].order.user.pk == request.user.pk
            ):
                return render(
                    request,
                    "dashboard/customer_order_detail.html",
                    {"order_items": order, "order": order[0].order},
                )
            else:
                return HttpResponse("Order not found", status=404)
        except OrderItem.DoesNotExist:
            return HttpResponse(status=404)
