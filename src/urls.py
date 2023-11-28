from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    # local apps
    path("products/", include("products.urls", namespace="products")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path(
        "communication/",
        include("communication.urls", namespace="communication"),
    ),
    path("cart/", include("cart.urls", namespace="cart")),
    path("order/", include("order.urls", namespace="order")),
    path("coupons/", include("coupons.urls", namespace="coupons")),
    path("", include("pages.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
