import itertools
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image


class AvailableProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(available=True)


class Category(models.Model):
    parent = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["name"])]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name

    # def get_absolute_url(self):
    #     return reverse("item:list_by_category", args=[self.slug])


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to="product_images",
        blank=True,
        null=True,
        default="no_image.png",
    )
    thumbnail = models.ImageField(
        upload_to="product_images", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        get_user_model(), related_name="products", on_delete=models.CASCADE
    )

    objects = models.Manager()
    availables = AvailableProductManager()

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return self.name

    def _generate_slug(self):
        value = self.name
        candidate = original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Product.objects.filter(slug=candidate).exists():
                break
            candidate = f"{original}{i}"

        self.slug = candidate

    def save(self, *args, **kwargs):
        if not self.pk:
            # on model creation, generate slug
            self._generate_slug()
        super(Product, self).save(*args, **kwargs)

    def make_thumbnail(self, image, default_size=(300, 300)):
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(default_size)

        thumbnail_io = BytesIO()
        img.save(thumbnail_io, "JPEG", quality=85)

        thumbnail = File(thumbnail_io, name=image.name)

        return thumbnail

    def get_absolute_url(self):
        return reverse("products:detail", args=[self.slug])

    def get_image_url(self):
        if self.image:
            return self.image.url
        return "https://via.placeholder.com/240x240.jpg"

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return self.thumbnail.url
            else:
                return "https://via.placeholder.com/240x240.jpg"

    @property
    def rating(self):
        reviews_total = 0
        for review in self.reviews.all():
            reviews_total += review.rating

        if reviews_total > 0:
            return reviews_total / self.reviews.count()

        return reviews_total


class CanReview(models.Model):
    product = models.ForeignKey(
        Product, related_name="can_review_users", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        get_user_model(),
        related_name="can_review_users",
        on_delete=models.CASCADE,
    )


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    content = models.TextField()
    created_by = models.ForeignKey(
        get_user_model(), related_name="reviews", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.content[:15]


class Favorite(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="favorites",
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        get_user_model(), related_name="favorites", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
