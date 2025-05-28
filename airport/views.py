from datetime import datetime
from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Ticket,
    Order,
)
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    FlightCreateUpdateSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateUpdateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateUpdateSerializer,
)


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminUser]


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = [IsAdminUser]


class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminUser]


class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminUser]


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAdminUser]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route",
        "airplane"
    ).prefetch_related(
        "crew"
    ).annotate(tickets_available=F(
        "airplane__rows"
    ) * F(
        "airplane__seats_in_row"
    ) - Count(
        "tickets"
    )
    )
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightCreateUpdateSerializer

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date")
        route_id = self.request.query_params.get("route")
        airplane_id = self.request.query_params.get("airplane")
        if date:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date_obj)
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if airplane_id:
            queryset = queryset.filter(airplane_id=airplane_id)
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                OpenApiTypes.DATE,
                description="Filter by date (YYYY-MM-DD)"
            ),
            OpenApiParameter(
                "route",
                OpenApiTypes.INT,
                description="Filter by route ID"
            ),
            OpenApiParameter(
                "airplane",
                OpenApiTypes.INT,
                description="Filter by airplane ID"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        total_seats = flight.airplane.rows * flight.airplane.seats_in_row
        booked_seats = flight.tickets.count()
        available = total_seats - booked_seats
        return Response({"available_seats": available})


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("flight", "order")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketCreateUpdateSerializer

    def get_queryset(self):
        queryset = self.queryset
        flight_id = self.request.query_params.get("flight")
        order_id = self.request.query_params.get("order")
        if flight_id:
            queryset = queryset.filter(flight_id=flight_id)
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "flight",
                OpenApiTypes.INT,
                description="Filter by flight ID"
            ),
            OpenApiParameter(
                "order",
                OpenApiTypes.INT,
                description="Filter by order ID"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.prefetch_related("tickets__flight")
    pagination_class = OrderPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderCreateUpdateSerializer

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def my_tickets(self, request):
        tickets = Ticket.objects.filter(order__user=request.user)
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)
