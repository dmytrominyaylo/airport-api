import os.path
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


def create_custom_path(instance, filename):
    _, extension = os.path.splitext(filename)
    model_lower = str(instance.__class__.__name__).lower() + "s_media_files"
    slug = str(instance)[:50]
    return os.path.join(
        f"uploads/{model_lower}/",
        f"{slugify(slug)}-{uuid.uuid4()}{extension}"
    )


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Airport"
        verbose_name_plural = "Airports"
        ordering = ["name"]
        db_table = "airport"

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )
    distance = models.IntegerField()

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        ordering = ["source", "destination"]
        db_table = "route"

    def __str__(self):
        return f"{self.source} - {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Airplane Type"
        verbose_name_plural = "Airplane Types"
        ordering = ["name"]
        db_table = "airplane_type"

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=create_custom_path
    )

    class Meta:
        verbose_name = "Airplane"
        verbose_name_plural = "Airplanes"
        ordering = ["name"]
        db_table = "airplane"

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Crew Member"
        verbose_name_plural = "Crew Members"
        ordering = ["first_name", "last_name"]
        db_table = "crew"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    class Meta:
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        ordering = ["departure_time"]
        db_table = "flight"

    def __str__(self):
        return f"Flight {self.id} on {self.route} at {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]
        db_table = "order"

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["flight", "row", "seat"]
        db_table = "ticket"
        unique_together = ("flight", "row", "seat")

    def __str__(self):
        return f"Seat {self.row} - {self.seat} on {self.flight}"

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        self.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )
        if self.flight.departure_time < timezone.now():
            raise ValidationError(
                "Cannot book a ticket: the flight has already departed."
            )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )
