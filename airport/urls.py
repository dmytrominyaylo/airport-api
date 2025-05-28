from django.urls import path, include
from rest_framework import routers
from airport.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
    TicketViewSet,
    OrderViewSet,
)

app_name = "airport"

router = routers.DefaultRouter()

router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register(
    "airplane-types", AirplaneTypeViewSet, basename="airplane_type"
)
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("crews", CrewViewSet, basename="crew")
router.register("flights", FlightViewSet, basename="flight")
router.register("tickets", TicketViewSet, basename="ticket")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [path("", include(router.urls))]
