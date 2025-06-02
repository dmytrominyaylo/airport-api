from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )

    def test_login_required_for_orders(self):
        response = self.client.get(reverse("airport:order-list"))
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_access_orders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("airport:order-list"))
        self.assertNotEqual(response.status_code, 403)
