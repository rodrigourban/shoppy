from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse
from datetime import datetime

from .models import Conversation, Message
from .forms import MessageForm
from products.models import Product



class ConversationListView(LoginRequiredMixin, ListView):
  model = Conversation
  template_name = 'communication/list.html'
  context_object_name = 'conversations'

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['has_unread_message'] = True
      context['last_message_created_at'] = datetime.now()
      context['last_message'] = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed augue augue, ultricies id sapien sit amet, interdum aliquet elit. Aenean vulputate dignissim semper. Nunc in convallis neque, vitae hendrerit libero. Donec in consectetur mi. Vestibulum tempor molestie tempor. Quisque scelerisque nec enim ut consequat."
      return context

class ConversationCreateView(LoginRequiredMixin, CreateView):
  model = Conversation
  template_name = 'communication/partials/_create_form.html'
  context_object_name = 'conversations'
  form_class = MessageForm

  def get_success_url(self):
    return reverse('communication:detail', self.pk)

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      product = get_object_or_404(
        Product,
        pk=self.kwargs['product_id']
      )
      context['product'] = product
      return context

  def form_valid(self, form):
    content = form.cleaned_data['content']
    product = Product.objects.get(pk=self.kwargs['product_id'])
    user_list = get_user_model().objects.filter(
      Q(pk=self.request.user.pk) | Q(is_superuser=True)
    )
    conversation = Conversation(product=product)
    conversation.add(user_list)
    conversation.save()
    message = Message.objects.create(
      conversation=conversation,
      content=content,
    )
    return super().form_valid(form)
  

class ConversationDetailView(LoginRequiredMixin, DetailView):
  model = Conversation
  template_name = 'communication/detail.html'
  context_object_name = 'conversation'

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      last_message = context['conversation'].messages.latest('created_at')
      if last_message.read == False:
        last_message.read = True
        last_message.save()
      context['form'] = MessageForm()
      return context


def create_conversation_form(request):
  pass