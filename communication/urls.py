from django.urls import path

from .views import ConversationListView, MessageCreateView, ConversationCreateView

app_name = 'communication'

urlpatterns = [
    path('', ConversationListView.as_view(), name='list'),
    path('detail_create/<int:conversation_id>/', MessageCreateView.as_view(), name='create_detail'),
    path('create/<int:product_id>/', ConversationCreateView.as_view(), name='create'),
]
