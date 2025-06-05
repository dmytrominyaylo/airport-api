from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from airport.models import Route, Airport


class RouteTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="adminpass"
        )
        self.airport1 = Airport.objects.create(name="Airport 1", closest_big_city="City A")
        self.airport2 = Airport.objects.create(name="Airport 2", closest_big_city="City B")
        self.route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=500
        )

    def test_route_list_requires_admin(self):
        response = self.client.get(reverse("airport:route-list"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_route_list(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("airport:route-list"))
        self.assertEqual(response.status_code, 200)
