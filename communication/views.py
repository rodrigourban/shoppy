from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView

from products.models import Product

from .forms import MessageForm
from .models import Conversation, Message


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = "communication/list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return Conversation.objects.filter(members__id=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ConversationCreateView(LoginRequiredMixin, CreateView):
    model = Conversation
    template_name = "communication/create.html"
    context_object_name = "conversations"
    form_class = MessageForm

    def get_success_url(self):
        return reverse("communication:detail", self.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, pk=self.kwargs["product_id"])
        context["product"] = product
        return context

    def form_valid(self, form):
        content = form.cleaned_data["content"]
        product = Product.objects.get(pk=self.kwargs["product_id"])
        user_list = (
            get_user_model()
            .objects.filter(Q(pk=self.request.user.pk) | Q(is_superuser=True))
            .values_list("pk", flat=True)
        )
        conversation = Conversation(product=product)
        conversation.save()
        conversation.members.add(*user_list)
        conversation.save()
        Message.objects.create(
            conversation=conversation,
            content=content,
            created_by=self.request.user,
        )
        return redirect(reverse("communication:create_detail", args=[conversation.pk]))


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "communication/detail.html"
    context_object_name = "message"
    form_class = MessageForm

    def get_success_url(self):
        return reverse(
            "communication:create_detail",
            args=[self.kwargs["conversation_id"]],
        )

    def form_valid(self, form):
        conversation = Conversation.objects.get(pk=self.kwargs["conversation_id"])
        form.instance.conversation = conversation
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conversation"] = get_object_or_404(
            Conversation, pk=self.kwargs["conversation_id"]
        )
        last_message = context["conversation"].latest_message
        if not last_message.read and last_message.created_by.pk != self.request.user.pk:
            last_message.read = True
            last_message.save()
        return context
