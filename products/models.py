from django.db import models
from django.core.files import File
from django.contrib.auth import get_user_model
from django.urls import reverse

from io import BytesIO
from PIL import Image

class Category(models.Model):
  parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
  name = models.CharField(max_length=200)
  slug = models.SlugField(max_length=200, unique=True)

  class Meta:
    ordering = ('name',)
    indexes = [
      models.Index(fields=['name'])
    ]
    verbose_name = 'category'
    verbose_name_plural = 'categories'


  def __str__(self) -> str:
      return self.name

  # def get_absolute_url(self):
  #     return reverse("item:list_by_category", args=[self.slug])

class Product(models.Model):
  name = models.CharField(max_length=200)
  slug = models.SlugField(max_length=200, unique=True)
  description = models.TextField(blank=True, null=True)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  available = models.BooleanField(default=True)
  stock = models.PositiveIntegerField()
  image = models.ImageField(upload_to='product_images', blank=True, null=True)
  thumbnail = models.ImageField(upload_to='product_images', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
  created_by = models.ForeignKey(get_user_model(), related_name='products', on_delete=models.CASCADE)

  class Meta:
    ordering = ('name',)
    indexes = [
      models.Index(fields=['id', 'slug']),
      models.Index(fields=['name']),
      models.Index(fields=['-created_at']),
    ]

  def __str__(self) -> str:
      return self.name

  def make_thumbnail(self, image, default_size=(300, 300)):
    img = Image.open(image)
    img.convert('RGB')
    img.thumbnail(default_size)

    thumbnail_io = BytesIO()
    img.save(thumbnail_io, 'JPEG', quality=85)

    thumbnail = File(thumbnail_io, name=image.name)

    return thumbnail

  # def get_absolute_url(self):
  #     return reverse("item:detail", args=[self.id, self.slug])
  
  def get_image_url(self):
    if self.image:
      print('returning', self.image.url)
      return self.image.url
    return 'https://via.placeholder.com/240x240.jpg'

  def get_thumbnail(self):
    if self.thumbnail:
      return self.thumbnail.url
    else:
      if self.image:
        self.thumbnail = self.make_thumbnail(self.image)
        self.save()

        return self.thumbnail.url
      else:
        return 'https://via.placeholder.com/240x240.jpg'

  def get_rating(self):
    reviews_total = 0
    for review in self.reviews.all():
      reviews_total += review.rating

    if reviews_total > 0:
      return reviews_total / self.reviews.count()

    return reviews_total
        
class Review(models.Model):
  class RatingChoices(models.IntegerChoices):
    BAD = 1
    NORMAL = 2
    GOOD = 3

  product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
  rating = models.IntegerField(choices=RatingChoices.choices)
  content = models.TextField()
  created_by = models.ForeignKey(get_user_model(), related_name='reviews', on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)