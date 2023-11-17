from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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
        _qs = Product.availables.all()

        filters = {}

        category = self.request.GET.get('category', None)
        price_from = self.request.GET.get('price_from', 1)
        price_to = self.request.GET.get('price_to', 10000)
        order_by = self.request.GET.get('order_by', None)

        filters['price__gte'] = price_from
        filters['price__lte'] = price_to

        if category:
            filters['category'] = int(category)

        _qs = _qs.filter(**filters)

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
        _qs = Product.availables.all()

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
            _qs = Product.availables.annotate(
                name_similarity=TrigramSimilarity('name', query),
                description_similarity=TrigramSimilarity('description', query)
            ).filter(q_chain)
        else:
            _qs = _qs.filter(q_chain)

        if order_by:
            _qs = _qs.order_by(order_by)

        return _qs

class ProductsDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        _qs = super().get_queryset()
        
        return _qs.prefetch_related('reviews')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_products = Product.availables.filter(
            category=context['product'].category).exclude(pk=context['product'].pk)[0:3]
        context['related_products'] = related_products
        context['score'] = Review.objects.filter(product=context['product'].pk).aggregate(
            Sum('rating')
        )
        if self.request.user.is_authenticated:
            context['favorited'] = Favorite.objects.filter(
                product=context['product'],
                created_by=self.request.user
            ).exists()

        print(context)

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
        f"""
        <div id="favorite_state" class="inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm focus:relative {'text-red-500 hover:text-red-700' if favorite else 'text-grey-500 hover:text-grey-700'}">
     <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
    </svg>   
    {'Unfavorite' if favorite else 'Favorite'}
    <div>
    """
    )

    