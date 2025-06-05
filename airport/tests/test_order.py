from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from airport.models import Order


class OrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.order = Order.objects.create(user=self.user)

    def test_order_list_requires_authentication(self):
        response = self.client.get(reverse("airport:order-list"))
        self.assertEqual(response.status_code, 403)

    def test_user_can_access_own_orders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("airport:order-list"))
        self.assertEqual(response.status_code, 200)
