from django.urls import path

from .views import (
    FavoriteListView,
    ProductsCreateView,
    ProductsDetailView,
    ProductsListView,
    ProductsSearchView,
    ProductUpdateView,
    toggle_favorite,
)

app_name = "products"

urlpatterns = [
    path("", ProductsListView.as_view(), name="list"),
    path("create/", ProductsCreateView.as_view(), name="create"),
    path("update/<int:pk>/", ProductUpdateView.as_view(), name="update"),
    path("search/", ProductsSearchView.as_view(), name="search_filter"),
    path("favorites/", FavoriteListView.as_view(), name="favorite_list"),
    path("<slug:slug>/", ProductsDetailView.as_view(), name="detail"),
    # htmx
    path("toggle-favorite/<int:pk>/", toggle_favorite, name="toggle_favorite"),
]
