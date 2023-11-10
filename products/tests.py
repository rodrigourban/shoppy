from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Review, Product, Favorite
class ProductTests(TestCase):
  @classmethod
  def setUpTestData(cls):
    # create product instances
    new_user = get_user_model().objects.create_user(
      username='customer',
      email='customer@gmail.com',
      password='customer123'
    )
    new_superuser = get_user_model().objects.create_superuser(
      username='admin',
      email='admin@gmail.com',
      password='admin123'
    )
    cls.category = Category.objects.create(
      name='clothes'
    )
    cls.product = Product.objects.create(
      name='Nike shoes',
      description='This are the famous nike shoes',
      slug='nike-shoes',
      price=14.5,
      stock=5,
      category=cls.category,
      created_by=new_superuser
    )
    cls.review = Review.objects.create(
      product=cls.product,
      created_by=new_user,
      rating=4,
      content='This are great shoes'
    )
    cls.favorite = Favorite.objects.create(
      product=cls.product,
      created_by=new_user
    )

  def test_product_display(self):
    self.assertEqual(self.product.name, 'Nike shoes')
    self.assertEqual(self.product.description, 'This are the famous nike shoes')
    self.assertEqual(self.product.price, 14.5)
    self.assertEqual(self.product.stock, 5)
    self.assertEqual(self.product.category.name, 'clothes')
    self.assertEqual(self.product.created_by.username, 'admin')
    
  def test_product_list_view(self):
    response = self.client.get(reverse('products:list'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Nike shoes')
    self.assertTemplateUsed(response, 'products/list.html')

  def test_product_detail_view(self):
    self.client.login(email='customer@gmail.com', password='customer123')
    response = self.client.get(self.product.get_absolute_url())
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Nike shoes')
    self.assertContains(response, 'Stock: 5')
    # self.assertContains(response, '5 stars')
    self.assertContains(response, '1 review')
    # self.assertContains(response, 'This are great shoes')
    self.assertContains(response, 'Add to Cart')
    self.assertTemplateUsed(response, 'products/detail.html')

  def test_product_detail_view_admin(self):
    self.client.login(email='admin@gmail.com', password='admin123')
    response = self.client.get(self.product.get_absolute_url())
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Nike shoes')
    self.assertContains(response, 'Edit')
    self.assertContains(response, 'Delete')
    self.assertNotContains(response, 'Add to Cart')
    self.assertNotContains(response, 'Add to Favorite')
    self.assertTemplateUsed(response, 'products/detail.html')
    self.client.logout()

  def test_product_detail_view_404(self):
    response = self.client.get('/products/not-found/')
    self.assertEqual(response.status_code, 404)

  def test_product_create_view_redirect_login(self):
    response = self.client.get(reverse('products:create'))
    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
      response,
      f"{reverse('account_login')}?next=/products/create/"
    )
    response = self.client.get(
      f"{reverse('account_login')}?next=/products/"
    )
    self.assertContains(response, 'Log in')
  
  def test_product_create_view_403(self):
    self.client.login(email='customer@gmail.com', password='customer123')
    response = self.client.get(reverse('products:create'))
    self.assertEqual(response.status_code, 403)
    self.client.logout()

  def test_product_create_view(self):
    self.client.login(email='admin@gmail.com', password='admin123')
    response = self.client.get(reverse('products:create'))
    # assert form
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Create new product')
    self.assertTemplateUsed(response, 'products/create.html')
    self.client.logout()

  def test_product_create_403(self):
    response = self.client.post(reverse('products:create'), {
      'name': 'Test product',
      'description': 'test description',
      'category': self.category.pk,
      'price': 20,
      'stock': 3,
    })
    self.assertEqual(response.status_code, 302) # redirect to login
    self.client.login(email='customer@gmail.com', password='customer123')
    response = self.client.post(reverse('products:create'), {
      'name': 'Test product',
      'description': 'test description',
      'category': self.category.pk,
      'price': 20,
      'stock': 3,
    })
    self.assertEqual(response.status_code, 403)
    self.client.logout()

  def test_product_create_duplicate_error(self):
    self.client.login(email='admin@gmail.com', password='admin123')
    response = self.client.post(reverse('products:create'), {
      'name': 'Test product',
      'description': 'test description',
      'category': self.category.pk,
      'price': 20,
      'stock': 3,
    })
    product = Product.objects.filter(name='Test product')
    self.assertEqual(len(product), 1)

  def test_product_create(self):
      response = self.client.post(reverse('products:create'), {
        'name': 'Test product',
        'description': 'test description',
        'category': self.category.pk,
        'price': 20,
        'stock': 3,
      })
      self.assertEqual(response.status_code, 302) # redirects to product list
      product = Product.objects.filter(name='Test product')
      self.assertIsNotNone(product)
  
  def test_product_update_view(self):
    self.client.login(email='admin@gmail.com', password='admin123')
    response = self.client.get(reverse('products:update', args=[self.product.pk]))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.product.name)
    self.assertTemplateUsed(response, 'products/update.html')

  def test_product_update_view_404(self):
    response = self.client.get('products/update/12341')
    self.assertEqual(response.status_code, 404)

  def test_product_update_403(self):
    self.client.logout()
    response = self.client.get(reverse('products:update', args=[self.product.pk]))
    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
      response,
      f"{reverse('account_login')}?next=/products/update/{self.product.pk}/"
    )
    response = self.client.get(
      f"{reverse('account_login')}?next=/update/{self.product.pk}/"
    )
    self.assertContains(response, 'Log in')
    self.client.login(email='customer@gmail.com', password='customer123')
    response = self.client.get(reverse('products:update', args=[self.product.pk]))
    self.assertEqual(response.status_code, 403)

  def test_product_update(self):
    self.client.login(email='admin@gmail.com', password='admin123')
    response = self.client.post(reverse('products:update', args=[self.product.pk]), { 
      'name': 'New product name',
      'description': 'new-product-name',
      'category': self.category.pk,
      'price': 25,
      'slug': 'nike-shoes',
      'stock': 3
    })
    updated_product = Product.objects.filter(id=self.product.pk)
    self.assertEqual(updated_product[0].stock, 3)
    self.assertEqual(updated_product[0].name, 'New product name')


  def test_product_update_stock_0_automatically_deactivate(self):
    self.client.login(email='admin@gmail.com', password='admin123')
    response = self.client.post(reverse('products:update', args=[self.product.pk]), {
      'name': 'Nike shoes',
      'description': 'test description',
      'slug': 'nike-shoes',
      'category': self.category.pk,
      'price': 25,
      'stock': 0,
    })
    product = Product.objects.filter(id=self.product.pk)
    self.assertEqual(product[0].stock, 0)
    self.assertEqual(product[0].available, False)


class FavoriteTests(TestCase):
  @classmethod
  def setUpTestData(cls):
    # create product instances
    new_user = get_user_model().objects.create_user(
      username='customer',
      email='customer@gmail.com',
      password='customer123'
    )
    new_superuser = get_user_model().objects.create_superuser(
      username='admin',
      email='admin@gmail.com',
      password='admin123'
    )
    cls.category = Category.objects.create(
      name='clothes'
    )
    cls.product = Product.objects.create(
      name='Nike shoes',
      description='This are the famous nike shoes',
      slug='nike-shoes',
      price=14.5,
      stock=5,
      category=cls.category,
      created_by=new_superuser
    )
    cls.favorite = Favorite.objects.create(
      product=cls.product,
      created_by=new_user
    )

  
  def test_favorite_list_view_403_redirect(self):
    response = self.client.get(reverse('products:favorite_list'))
    self.assertEqual(response.status_code, 302)

  def test_favorite_list_view(self):
    self.client.login(email='customer@gmail.com', password='customer123')
    response = self.client.get(reverse('products:favorite_list'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Nike shoes')
    self.assertTemplateUsed(response, 'products/favorite_list.html')

  def test_favorite_toggle_403(self):
    self.client.logout()
    response = self.client.get(reverse('products:toggle_favorite', args=[self.product.pk]))
    self.assertEqual(response.status_code, 302) # redirect to login

  def test_favorite_toggle(self):
    self.client.logout()
    self.client.login(email='customer@gmail.com', password='customer123')
    response = self.client.get(reverse('products:toggle_favorite', args=[self.product.pk]))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Add to favorite')
    response = self.client.get(reverse('products:toggle_favorite', args=[self.product.pk]))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Remove favorite')


