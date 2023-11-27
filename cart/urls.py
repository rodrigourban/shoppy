from django.urls import path

from .views import CartListView, CartAddView, CheckoutView, CartUpdateView, HxMenuCart, HxTotalCost, SuccessView

app_name = 'cart'

urlpatterns = [
    path('', CartListView.as_view(), name='list'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add/<int:product_id>/', CartAddView.as_view(), name='add'),
    path('update_cart/<int:product_id>/<str:action>/', CartUpdateView.as_view(), name='update'),
    path('hx_menu_cart/', HxMenuCart.as_view(), name='hx_menu_cart'),
    path('hx_total_cost/', HxTotalCost.as_view(), name='hx_total_cost'),
    path('success/', SuccessView.as_view(), name='success'),
]
