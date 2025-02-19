from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError

from core.validators import validate_iata_code_format, validate_flight_number_format

SEATS_CLASS_CHOICES = [
    ("EC", "Economy Class"),
    ("BC", "Business Class"),
    ("FC", "First Class"),
]


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    iata_code = models.CharField(
        max_length=3,
        validators=[validate_iata_code_format],
        unique=True
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="airports"
    )

    class Meta:
        ordering = ("city__country", "city__name", "name")

    def __str__(self) -> str:
        return f"{self.name} {self.iata_code}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routes"
    )
    distance = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Distance in kilometers"
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=["source", "destination"],
                name="unique_route_source_destination"
            ),
        )
        ordering = ("source",)

    @staticmethod
    def validate_source_and_destination(
            source: Airport,
            destination: Airport,
            error_to_raise
    ) -> None:
        if source == destination:
            raise error_to_raise("The source can`t equal destination.")

    def clean(self) -> None:
        Route.validate_source_and_destination(
            self.source,
            self.destination,
            ValidationError
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Route, self).save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"{self.source.name} - {self.destination.name}"


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class CrewMember(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="members"
    )

    class Meta:
        ordering = ("role__name", "first_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.role.name})"


class CrewGroup(models.Model):
    pilots = models.ManyToManyField(
        CrewMember,
        related_name="pilot_crew_groups",
        blank=True
    )
    stewards = models.ManyToManyField(
        CrewMember,
        related_name="steward_crew_groups",
        blank=True
    )
    technicians = models.ManyToManyField(
        CrewMember,
        related_name="technician_crew_groups",
        blank=True
    )
    additional_staff = models.ManyToManyField(
        CrewMember,
        related_name="additional_staff_crew_groups",
        blank=True
    )

    def __str__(self) -> str:
        try:
            return f"Crew of flight {self.flight.flight_number}"
        except CrewGroup.flight.RelatedObjectDoesNotExist:
            return "Unassigned crew"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    model_name = models.CharField(max_length=255)
    type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    class Meta:
        ordering = ("type__name", "model_name")

    def __str__(self) -> str:
        return self.model_name


class SeatConfiguration(models.Model):
    seats_class = models.CharField(
        max_length=2,
        choices=SEATS_CLASS_CHOICES,
        default="EC"
    )
    rows = models.IntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.IntegerField(validators=[MinValueValidator(1)])
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="seats_configuration"
    )

    class Meta:
        ordering = (
            "airplane__model_name",
            models.Case(
                models.When(seats_class="EC", then=0),
                models.When(seats_class="BC", then=1),
                models.When(seats_class="FC", then=2),
                output_field=models.IntegerField()
            ),
        )

    @property
    def num_of_seats(self):
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.get_seats_class_display()} Configuration ({self.airplane.model_name})"


class Flight(models.Model):
    STATUS_CHOICES = [
        ("SD", "Scheduled"),
        ("AD", "Arrived"),
        ("CD", "Canceled"),
    ]
    flight_number = models.CharField(
        max_length=7,
        validators=[validate_flight_number_format],
        unique=True
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.SET_NULL,
        related_name="flights",
        null=True,
        blank=True
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default="SD"
    )
    crew = models.OneToOneField(
        CrewGroup,
        on_delete=models.SET_NULL,
        related_name="flight",
        null=True,
        blank=True
    )

    class Meta:
        ordering = (
            models.Case(
                models.When(status="SD", then=0),
                models.When(status="AD", then=1),
                models.When(status="CD", then=2),
                output_field=models.IntegerField()
            ),
            "departure_time"
        )

    def clean(self):
        if self.departure_time > self.arrival_time:
            raise ValidationError("Departure can`t be later than arrival.")

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Flight, self).save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return (f"Flight {self.flight_number} ({self.route}) "
                f"{self.departure_time} - {self.arrival_time}")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    passenger_first_name = models.CharField(max_length=255)
    passenger_last_name = models.CharField(max_length=255)
    seat_class = models.CharField(
        max_length=2,
        choices=SEATS_CLASS_CHOICES,
        default="EC"
    )
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
        constraints = (
            UniqueConstraint(
                fields=["flight", "seat_class", "seat"],
                name="unique_flight_seat"
            ),
        )
        ordering = ("seat",)

    def clean(self) -> None:
        if not self.flight.airplane:
            raise ValidationError("No airplane has been assigned to  this flight yet.")

        seat_configuration = self.flight.airplane.seats_configuration.filter(
            seats_class=self.seat_class
        ).first()

        if not seat_configuration:
            raise ValidationError(f"Seat configuration for {self.seat_class} not found.")

        max_seats = seat_configuration.num_of_seats
        max_rows = seat_configuration.rows

        if not (1 <= self.seat <= max_seats):
            raise ValidationError(f"Seat must be in range [1, {max_seats}].")

        if not (1 <= self.row <= max_rows):
            raise ValidationError(f"Row must be in range [1, {max_rows}].")

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"Flight: {self.flight.flight_number} (row: {self.row}, seat: {self.seat})"
