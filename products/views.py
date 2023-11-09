from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Favorite, Product, Category, Review
from .forms import ProductCreateForm, ProductUpdateForm


class ProductsListView(ListView):
    model = Product
    context_object_name = 'product_list'
    template_name = 'products/list.html'
    paginate_by = 10

    def get_queryset(self):
        filter_by = self.request.GET('filter', None)
        order_by = self.request.GET('orderby', None)
        page = self.request.GET('page', None)
        print(f'filter {filter_by} order_by {order_by} page {page}')
        # new_context = Product.objects.filter(
        #     filter_by=filter_by
        # ).order_by(order_by)
        return super().get_queryset()

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
        if self.request.user.is_authenticated:
            context['favorited'] = Favorite.objects.filter(
                product=context['product'],
                created_by=self.request.user
            ).exists()
        # select_related / fetch_related ?
        print("context", context)
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

class FavoriteListView(
    LoginRequiredMixin,
    ListView):
    model = Favorite
    template_name = 'products/favorite_list.html'
    context_object_name = 'favorite_list'

    def get_queryset(self):
        print(self.request.user)
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

