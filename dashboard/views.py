from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from products.models import Product


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(created_by=self.request.user)
        return context
