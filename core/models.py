from django.conf import settings
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    iata_code = models.CharField(max_length=3, unique=True)
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
    distance = models.IntegerField()

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
        if self.flight:
            return f"Crew of flight {self.flight.flight_number}"
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
    SEATS_CLASS_CHOICES = [
        ("EC", "Economy Class"),
        ("BC", "Business Class"),
        ("FC", "First Class"),
    ]
    seats_class = models.CharField(
        max_length=2,
        choices=SEATS_CLASS_CHOICES,
        default="EC"
    )
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
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

    def __str__(self) -> str:
        return f"{self.get_seats_class_display()} Configuration ({self.airplane.model_name}"


class Flight(models.Model):
    STATUS_CHOICES = (
        ("SD", "Scheduled"),
        ("AD", "Arrived"),
        ("CD", "Canceled"),
    )
    flight_number = models.CharField(max_length=7, unique=True)
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
