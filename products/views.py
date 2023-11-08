from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse

from .models import Product, Category, Review
from .forms import ProductCreateForm, ProductUpdateForm


class ProductsListView(ListView):
    model = Product
    context_object_name = 'product_list'
    template_name = 'products/list.html'
    paginate_by = 10

    # def get_queryset(self):
    #     filter_by = self.request.GET('filter', None)
    #     order_by = self.request.GET('orderby', None)
    #     new_context = Product.objects.filter(
    #         filter_by=filter_by
    #     ).order_by(order_by)
    #     return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.filter(active=True)
        context['categories'] = categories
        return context


class ProductsDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_products = Product.objects.filter(
            category=context['product'].category, available=True).exclude(pk=context['product'].pk)[0:3]
        context['related_products'] = related_products
        print(context)
        return context

class ProductsCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView):
    model = Product
    login_url = 'account_login'
    template_name = 'products/create.html'
    form_class = ProductCreateForm
    permission_required = 'products:add_product'
    
    def get_success_url(self):
        return reverse('products:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    

class ProductUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView):
    model = Product
    login_url = 'account_login'
    template_name = 'products/update.html'
    form_class = ProductUpdateForm
    permission_required = 'products:change_product'

    def get_success_url(self):
        return reverse('products:list')
    

