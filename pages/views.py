from typing import Any
from django.views.generic import TemplateView

from products.models import Product


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["products"] = Product.availables.all().order_by("-created_at")[:4]
        context["featured_products"] = Product.availables.filter(featured=True)[:2]
        return context


class AboutPageView(TemplateView):
    template_name = "about.html"


class FAQPageView(TemplateView):
    template_name = "faq.html"
