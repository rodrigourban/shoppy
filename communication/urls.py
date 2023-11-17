from django.urls import path

from .views import ConversationListView, ConversationDetailView, ConversationCreateView

app_name = 'communication'

urlpatterns = [
    path('', ConversationListView.as_view(), name='list'),
    path('detail/<int:pk>/', ConversationDetailView.as_view(), name='detail'),
    path('create/<int:product_id>/', ConversationCreateView.as_view(), name='create'),
]
