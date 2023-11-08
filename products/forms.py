from django import forms

from .models import Product

INPUT_CLASSES = 'mt-1 w-full rounded-md border-gray-200 shadow-sm sm:text-sm'

class ProductCreateForm(forms.ModelForm):
  class Meta:
    model = Product
    fields = ('category', 'name', 'description', 'price', 'image', 'stock')

    widgets = {
      'category': forms.Select(attrs={
        'class': INPUT_CLASSES
      }),
      'name': forms.TextInput(attrs={
        'class': INPUT_CLASSES
      }),
      'description': forms.Textarea(attrs={
        'class': INPUT_CLASSES
      }),
      'price': forms.TextInput(attrs={
        'class': INPUT_CLASSES
      }),
      'image': forms.FileInput(attrs={
        'class': INPUT_CLASSES
      }),
    }


class ProductUpdateForm(forms.ModelForm):
  class Meta:
    model = Product
    fields = ('category', 'name', 'description', 'price', 'image', 'stock', 'available')

    widgets = {
      'name': forms.TextInput(attrs={
        'class': INPUT_CLASSES
      }),
      'description': forms.Textarea(attrs={
        'class': INPUT_CLASSES
      }),
      'price': forms.TextInput(attrs={
        'class': INPUT_CLASSES
      }),
      'stock': forms.TextInput(attrs={
        'class': INPUT_CLASSES
      }),
      'image': forms.FileInput(attrs={
        'class': INPUT_CLASSES
      }),
    }