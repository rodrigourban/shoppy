from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Conversation, Message
from products.models import Product, Category

CATEGORY_1 = {
  'name': 'beverages',
  'slug': 'beverages'
}

USER_CUSTOMER = {
  'username': 'John State',
  'email': 'johnstate@gmail.com',
  'password': 'johnstate123'
}

USER_ADMIN = {
  'username':'admin',
  'email':'admin@gmail.com',
  'password':'admin123'
}

USER_ADMIN_2 = {
  'username':'manager',
  'email':'manager@gmail.com',
  'password':'manager123'
}

MESSAGE_1 = {
  'content': "Hello, I want to ask a question regarding this tea"
}

MESSAGE_2 = {
  'content': "Sure, I'm glad I can help you. What's your question?"
}

PRODUCT_1 = {
  'name': 'Green tea',
  'slug': 'green-tea',
  'description': 'Great beverage that helps you stay healthy',
  'price': 5.5,
  'stock': 1,
}

class CustomerCommunicationTests(TestCase):
  @classmethod
  def setUpTestData(cls) -> None:
    cls.user = get_user_model().objects.create_user(**USER_CUSTOMER)
    cls.superuser = get_user_model().objects.create_superuser(**USER_ADMIN)
    cls.superuser2 = get_user_model().objects.create_superuser(**USER_ADMIN_2)
    cls.category = Category.objects.create(**CATEGORY_1)
    cls.product = Product.objects.create(
      **PRODUCT_1,
      category=cls.category,
      created_by=cls.superuser
    )
    cls.url_list = reverse('communication:list')

  def test_communications_list_view_403(self):
    response = self.client.get(self.url_list)
    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
      response,
      f"{reverse('account_login')}?next=/communication/"
    )

  def test_communications_list_view_no_conversations(self):
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.get(self.url_list)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Messages')
    self.assertContains(response, "No conversations yet.")
    self.assertTemplateUsed(response, 'communication/list.html')

  def test_communications_create_view_403(self):
    response = self.client.get(reverse('communication:create_detail', args=[1]))
    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
      response,
      f"{reverse('account_login')}?next=/communication/create_detail/1/"
    )
  
  def test_communications_create_view_404(self):
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.get(reverse('communication:create_detail', args=[1231312]))
    self.assertEqual(response.status_code, 404)

  def test_communications_create_view(self):
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.get(reverse('communication:create', args=[self.product.pk]))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Ask a question')
    self.assertTemplateUsed(response, 'communication/create.html')

  def test_communications_create(self):
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.post(reverse('communication:create', args=[self.product.pk]), MESSAGE_1)
    self.assertEqual(response.status_code, 302) # redirect to dashboard
    conversation = Conversation.objects.first()
    self.assertEqual(Conversation.objects.count(), 1)
    self.assertEqual(Message.objects.count(), 1)
    self.assertEqual(conversation.members.count(), 3) # user and all superusers

  def test_communications_list_view(self):
    conversation = Conversation.objects.create(
      product=self.product
    )
    conversation.members.add(self.user, self.superuser, self.superuser2)
    new_message = Message.objects.create(
      content=MESSAGE_1['content'],
      read=True,
      conversation=conversation,
      created_by=self.user
    )
    new_message_2 = Message.objects.create(
      content=MESSAGE_2['content'],
      conversation=conversation,
      read=True,
      created_by=self.superuser2
    )
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.get(self.url_list)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Messages')
    self.assertContains(response, PRODUCT_1['name'])
    self.assertContains(response, 'Sent on')
    self.assertNotContains(response, 'New message')

  def test_communications_list_view_unread_notification(self):
    conversation = Conversation.objects.create(
      product=self.product
    )
    conversation.members.add(self.user, self.superuser, self.superuser2)
    new_message = Message.objects.create(
      content=MESSAGE_1['content'],
      conversation=conversation,
      created_by=self.user
    )
    new_message_2 = Message.objects.create(
      content=MESSAGE_2['content'],
      conversation=conversation,
      created_by=self.superuser2
    )
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.get(self.url_list)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Messages')
    self.assertContains(response, PRODUCT_1['name'])
    self.assertContains(response, 'Sent on')
    self.assertContains(response, 'New message')
    self.assertContains(response, f'{new_message_2.created_at.strftime("%d/%m/%Y %H:%M")}')

  def test_communications_list_view_mark_as_read(self):
    conversation = Conversation.objects.create(
      product=self.product
    )
    conversation.members.add(self.user, self.superuser, self.superuser2)
    new_message = Message.objects.create(
      content=MESSAGE_1['content'],
      conversation=conversation,
      created_by=self.user,
      read=True
    )
    new_message_2 = Message.objects.create(
      content=MESSAGE_2['content'],
      conversation=conversation,
      created_by=self.superuser2,
      read=False
    )
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.get(reverse('communication:create_detail', args=[conversation.pk])) # open unread message
    response = self.client.get(self.url_list)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Messages')
    self.assertContains(response, PRODUCT_1['name'])
    self.assertContains(response, 'Sent on')
    self.assertContains(response, f'{new_message_2.created_at.strftime("%d/%m/%Y %H:%M")}')
    self.assertNotContains(response, 'New message')

  def test_communications_detail_view_403(self):
    self.client.logout()
    response = self.client.get(reverse('communication:create_detail', args=[1]))
    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
      response,
      f"{reverse('account_login')}?next=/communication/create_detail/1/"
    )
  
  def test_communications_detail_view_404(self):
    self.client.login(email=USER_CUSTOMER['email'], password=USER_CUSTOMER['password'])
    response = self.client.get(reverse('communication:create_detail', args=[1231312]))
    self.assertEqual(response.status_code, 404)


class AdminCommunicationTests(TestCase):
  @classmethod
  def setUpTestData(cls):
    cls.user = get_user_model().objects.create_user(**USER_CUSTOMER)
    cls.superuser = get_user_model().objects.create_superuser(**USER_ADMIN)
    cls.superuser2 = get_user_model().objects.create_superuser(**USER_ADMIN_2)
    cls.category = Category.objects.create(**CATEGORY_1)
    cls.product = Product.objects.create(
      **PRODUCT_1,
      category=cls.category,
      created_by=cls.superuser
    )
    cls.url_list = reverse('communication:list')

  
  def test_communications_list_view_no_conversations(self):
    self.client.login(username=USER_ADMIN['username'], password=USER_ADMIN['password'])
    response = self.client.get(self.url_list)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Admin Messages')
    self.assertContains(response, "No conversations yet.")
    self.assertTemplateUsed(response, 'communication/list.html')

  def test_communications_list_view_both_admins(self):
    # show for both admins
    pass

  def test_communications_list_create_as_admin(self):
    # should post message as admin
    pass
