from django.urls import path

from .views import CartListView, add, list, checkout, hx_menu_cart, update_cart, hx_total_cost, success

app_name = 'cart'

urlpatterns = [
    path('', CartListView.as_view(), name='list'),
    path('checkout/', checkout, name='checkout'),
    path('add/<int:product_id>/', add, name='add'),
    path('update_cart/<int:product_id>/<str:action>/', update_cart, name='update_cart'),
    path('hx_menu_cart/', hx_menu_cart, name='hx_menu_cart'),
    path('hx_total_cost/', hx_total_cost, name='hx_total_cost'),
    path('success/', success, name='success'),
]
