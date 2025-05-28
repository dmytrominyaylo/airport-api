from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User
from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type"]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class FlightListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ["id", "departure_time", "arrival_time", "route"]


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = AirplaneSerializer()
    crew = CrewSerializer(many=True)

    class Meta:
        model = Flight
        fields = [
            "id", "route", "airplane",
            "departure_time", "arrival_time",
            "crew"
        ]


class FlightCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "route", "airplane", "departure_time", "arrival_time", "crew"
        ]


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]


class TicketDetailSerializer(serializers.ModelSerializer):
    flight = FlightDetailSerializer()
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]


class TicketCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["row", "seat", "flight", "order"]

    def validate(self, attrs):
        row = attrs.get("row")
        seat = attrs.get("seat")
        order = attrs.get("order")
        flight = attrs.get("flight")
        if not all([row, seat, order, flight]):
            raise serializers.ValidationError(
                "row, seat, flight and order are required."
            )
        Ticket.validate_ticket(
            row=row,
            seat=seat,
            order=order,
            flight=flight,
            error_class=serializers.ValidationError
        )
        return attrs


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "created_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    tickets = TicketListSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user", "tickets"]


class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateUpdateSerializer(many=True)

    class Meta:
        model = Order
        fields = ["tickets"]

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user
        with transaction.atomic():
            order = Order.objects.create(user=user, **validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
        return order
