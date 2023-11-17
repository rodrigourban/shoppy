from django.contrib import admin

from .models import Category, Product, Review, Favorite

class ReviewInline(admin.StackedInline):
    model = Review
    extra = 3

class FavoriteInline(admin.StackedInline):
    model = Favorite
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price',
                    'available', 'created_at', 'updated_at', 'stock']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'available', 'stock']
    prepopulated_fields = {'slug': ('name',)}

    inlines = [ReviewInline, FavoriteInline]
