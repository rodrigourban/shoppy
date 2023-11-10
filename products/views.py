from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse

from .models import Favorite, Product, Category, Review
from .forms import ProductCreateForm, ProductUpdateForm


class ProductsListView(ListView):
    model = Product
    context_object_name = 'product_list'
    template_name = 'products/list.html'
    paginate_by = 15

    def get_queryset(self):
        filters = {'available': True}
        category = self.request.GET.get('category', None)
        price_from = self.request.GET.get('price_from', 1)
        price_to = self.request.GET.get('price_to', 10000)
        order_by = self.request.GET.get('order_by', None)

        filters['price__gte'] = price_from
        filters['price__lte'] = price_to

        if category:
            filters['category'] = int(category)
        _qs = Product.objects.filter(**filters)

       
        if order_by:
            _qs = _qs.order_by(order_by)

        return _qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.filter(active=True)
        context['categories'] = categories
        return context

class ProductsSearchView(ListView):
    model = Product
    context_object_name = 'product_list'
    template_name = 'products/partials/_list.html'
    paginate_by = 15

    def get_queryset(self):
        q_chain = Q(available=True)
        category = self.request.GET.get('category', None)
        price_from = self.request.GET.get('price_from', 1)
        price_to = self.request.GET.get('price_to', 10000)
        order_by = self.request.GET.get('order_by', None)
        query = self.request.GET.get('query', None)

        q_chain &= Q(price__gte=price_from)
        q_chain &= Q(price__lte=price_to)

        if category:
            q_chain &= Q(category=int(category))

        if query:
            q_chain &= Q(Q(name_similarity__gt=0.1) | Q(description_similarity__gt=0.1))
            _qs = Product.objects.annotate(
                name_similarity=TrigramSimilarity('name', query),
                description_similarity=TrigramSimilarity('description', query)
            ).filter(q_chain)
        else:
            _qs = Product.objects.filter(q_chain)

        if order_by:
            _qs = _qs.order_by(order_by)

        return _qs

class ProductsDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_products = Product.objects.filter(
            category=context['product'].category, available=True).exclude(pk=context['product'].pk)[0:3]
        context['related_products'] = related_products
        if self.request.user.is_authenticated:
            context['favorited'] = Favorite.objects.filter(
                product=context['product'],
                created_by=self.request.user
            ).exists()
        # select_related / fetch_related ?
        return context

class ProductsCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView):
    model = Product
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
    template_name = 'products/update.html'
    form_class = ProductUpdateForm
    permission_required = 'products:change_product'

    def get_success_url(self):
        return reverse('products:list')

    def form_valid(self, form):
        if form.instance.stock <= 0:
            form.instance.available = False
        return super().form_valid(form)

class FavoriteListView(
    LoginRequiredMixin,
    ListView):
    model = Favorite
    template_name = 'products/favorite_list.html'
    context_object_name = 'favorite_list'

    def get_queryset(self):
        favorite_list = Favorite.objects.filter(
            created_by=self.request.user
        )
        return favorite_list

@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, id=pk)
    try:
        favorite = Favorite.objects.get(
            product=product,
            created_by=request.user
        )
        favorite.delete()
        favorite = False
    except Favorite.DoesNotExist:
        favorite = Favorite.objects.create(
            product=product,
            created_by=request.user
        )
        favorite = True

    
    return HttpResponse(
        f"""<div id="favorite_state" class="flex {'text-red-500 hover:text-red-700' if favorite else 'text-grey-500 hover:text-grey-700'}">
    <svg fill="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="w-5 h-5 mr-1" viewBox="0 0 24 24">
      <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"></path>
    </svg>
    {'Remove favorite' if favorite else 'Add to favorite'}
    <div>
    """
    )
