from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
from airport.models import Flight, Route, Airplane, Airport, AirplaneType


class FlightTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="adminpass"
        )
        self.airport1 = Airport.objects.create(name="Airport 1", closest_big_city="CityA")
        self.airport2 = Airport.objects.create(name="Airport 2", closest_big_city="CityB")
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=500
        )
        self.airplane_type = AirplaneType.objects.create(name="Passenger")
        self.airplane = Airplane.objects.create(
            name="Boeing",
            rows=20,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.make_aware(datetime.datetime(
                2025,
                6,
                10,
                10,
                0,
                0
            )),
            arrival_time=timezone.make_aware(datetime.datetime(
                2025,
                6,
                10,
                14,
                0,
                0
            ))
        )

    def test_flight_list_requires_admin(self):
        response = self.client.get(reverse("airport:flight-list"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_flight_list(self):
        self.client.login(email="admin@example.com", password="adminpass")
        response = self.client.get(reverse("airport:flight-list"))
        self.assertEqual(response.status_code, 200)
