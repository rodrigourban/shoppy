from django.urls import path

from .views import AboutPageView, FAQPageView, HomePageView

app_name = "pages"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("faq/", FAQPageView.as_view(), name="faq"),
]
