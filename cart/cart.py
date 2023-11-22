from decimal import Decimal
from django.conf import settings

from products.models import Product
# from coupons.models import Coupon

class Cart(object):
  def __init__(self, request):
    self.cart_session_id = getattr(settings,'CART_SESSION_ID', 'test') # For testing purposes, set default
    self.session = request.session
    cart = self.session.get(self.cart_session_id)

    if not cart:
      cart = self.session[self.cart_session_id] = {}
    
    self.cart = cart

    # coupons
    # self.coupon_id = self.session.get('coupon_id')


  def __iter__(self):
    for product_id in self.cart.keys():
      self.cart[str(product_id)]['properties'] = Product.objects.get(pk=product_id)

    for product in self.cart.values():
      product['total_price'] = product['properties'].price + product['quantity']

      yield product


  def __len__(self):
    return sum(product['quantity'] for product in self.cart.values())

  # @property
  # def coupon(self):
  #   if self.coupon_id:
  #     try:
  #       return Coupon.objects.get(id=self.coupon_id)
  #     except Coupon.DoesNotExist:
  #       pass
  #   return None

  # def get_discount(self):
  #   if self.coupon:
  #     return (self.coupon.discount  / Decimal(100)) * self.get_total_cost()
  #   return Decimal(0)

  # def get_total_price_after_discount(self):
  #   return self.get_total_cost() - self.get_discount()

  def save(self):
    self.session[self.cart_session_id] = self.cart
    self.session.modified = True

  def add(self, product_id, quantity=1, update_quantity=False):
    product_id = str(product_id)

    if product_id not in self.cart:
      self.cart[product_id] = {
        'quantity': quantity,
        'id': product_id,
      }

    if update_quantity:
      self.cart[product_id]['quantity'] += int(quantity)

      if self.cart[product_id]['quantity'] == 0:
        self.remove(product_id)

    self.save()

  def remove(self, product_id):
    if product_id in self.cart:
      del self.cart[product_id]
      self.save()

  def clear(self):
    del self.session[self.cart_session_id]
    self.session.modified = True

  def get_total_cost(self):
    for product_id in self.cart.keys():
      self.cart[str(product_id)]['properties'] = Product.objects.get(pk=product_id)

    return sum(product['properties'].price * product['quantity'] for product in self.cart.values())

  def get_product(self, product_id):
    print("Hey", self.cart[str(product_id)])
    print("Hey", self.cart)
    return self.cart[str(product_id)]