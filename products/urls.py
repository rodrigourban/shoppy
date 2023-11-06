from django.urls import path

from .views import detail, new, delete, edit, list

app_name = 'products'

urlpatterns = [
    path('', list, name='list'),
    path('<int:pk>/', detail, name='detail'),
    # path('<slug:category_slug>/', list, name='list_by_category'),
    # path('<int:pk>/<slug:slug>/', detail, name='item_detail'),
    path('new/', new, name='new'),
    path('delete/<int:pk>/', delete, name='delete'),
    path('edit/<int:pk>/', edit, name='edit'),
]
