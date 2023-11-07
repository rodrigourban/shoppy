from django.urls import path

from .views import ProductsDetailView, new, delete, edit, ProductsListView

app_name = 'products'

urlpatterns = [
    path('', ProductsListView.as_view(), name='list'),
    path('<slug:slug>/', ProductsDetailView.as_view(), name='detail'),
    # path('<slug:category_slug>/', list, name='list_by_category'),
    # path('<int:pk>/<slug:slug>/', detail, name='item_detail'),
    path('new/', new, name='new'),
    path('delete/<int:pk>/', delete, name='delete'),
    path('edit/<int:pk>/', edit, name='edit'),
]
