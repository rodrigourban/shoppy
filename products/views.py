from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView

from .models import Product, Category, Review
from .forms import NewProductForm, EditProductForm


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


def detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # review
        rating = request.POST.get('rating', 3)
        content = request.POST.get('content')

        if content:
            review = Review.objects.create(
                product=product,
                rating=rating,
                content=content,
                created_by=request.user
            )

            return redirect('product:detail', product.id)

    related_products = Product.objects.filter(
        category=product.category, available=True).exclude(pk=pk)[0:3]

    return render(request, 'products/detail.html', {'product': product, 'related_products': related_products})


@login_required
def new(request):
    if request.method == 'POST':
        form = NewProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()

            return redirect('product:detail', pk=product.id)
    else:
        form = NewProductForm()

    return render(
        request,
        'products/new_product.html',
        {
            'form': form,
            'title': 'Add a new product'
        }
    )


@login_required
def delete(request, pk):
    product = get_object_or_404(Product, pk=pk, created_by=request.user)
    product.delete()

    return redirect('dashboard:index')


@login_required
def edit(request, pk):
    product = get_object_or_404(Product, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()

            return redirect('product:detail', pk=product.id)
    else:
        form = EditProductForm(instance=product)

    return render(
        request,
        'products/new_product.html',
        {
            'form': form,
            'title': 'Edit product'
        }
    )


# def product_list(request, category_slug=None):
#     category = None
#     categories = Category.objects.all()
#     products = Product.objects.filter(available=True)
#     if category_slug:
#         category = get_object_or_404(Category,
#                                      slug=category_slug)
#         products = products.filter(category=category)
#     return render(request,
#                   'shop/products/list.html',
#                   {'category': category,
#                       'categories': categories,
#                       'products': products})

# def product_detail(request, id, slug):
#     product = get_object_or_404(Product,
#                                 id=id,
#                                 slug=slug,
#                                 available=True)
#     return render(request,
#                   'shop/products/detail.html',
#                   {'product': product})