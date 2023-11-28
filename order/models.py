from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from coupons.models import Coupon
from products.models import Product


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        ORDERED = "ordered", "Ordered"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        get_user_model(),
        related_name="orders",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    paid = models.BooleanField(default=False)
    paid_amount = models.FloatField(blank=True, null=True)
    shipping_cost = models.FloatField(blank=True, null=True)
    coupon = models.ForeignKey(
        Coupon,
        related_name="orders",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    status = models.CharField(
        max_length=25, choices=StatusChoices.choices, default="ordered"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Order {self.id} {self.email}"

    def get_total_cost(self):
        if self.paid_amount:
            return self.paid_amount

        return 0

    # def get_total_cost_before_discount(self):
    #   return sum(product.get_cost() for product in self.products.all())

    # def get_discount(self):
    #   total_cost = self.get_total_cost_before_discount()
    #   if self.discount:
    #       return total_cost * (self.discount / Decimal(100))
    #   return Decimal(0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="orders", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="products", on_delete=models.CASCADE
    )
    price = models.FloatField()
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order product {self.id}"
