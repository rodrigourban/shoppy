from django.urls import path

from .views import ProductsDetailView, ProductsListView, ProductsCreateView, ProductUpdateView

app_name = 'products'

urlpatterns = [
    path('', ProductsListView.as_view(), name='list'),
    path('create/', ProductsCreateView.as_view(), name='create'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='update'),
    path('<slug:slug>/', ProductsDetailView.as_view(), name='detail'),
]
