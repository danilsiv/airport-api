from rest_framework import serializers
from django.db import transaction

from core.validators import validate_seat_class
from core.models import (
    City,
    Airport,
    Route,
    Role,
    CrewMember,
    CrewGroup,
    AirplaneType,
    Airplane,
    SeatConfiguration,
    Flight, Ticket, Order, SEATS_CLASS_CHOICES,
)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "iata_code", "city")


class AirportListSerializer(AirportSerializer):
    city = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class AirportRetrieveSerializer(AirportSerializer):
    city = CitySerializer()


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, attrs) -> None:
        Route.validate_source_and_destination(
            attrs["source"],
            attrs["destination"],
            serializers.ValidationError
        )


class RouteListSerializer(serializers.ModelSerializer):
    source = AirportListSerializer()
    destination = AirportListSerializer()

    class Meta:
        model = Route
        fields = ("id", "route_code", "source", "destination", "distance")


class RouteRetrieveSerializer(RouteListSerializer):
    source = AirportRetrieveSerializer()
    destination = AirportRetrieveSerializer()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name")


class CrewMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewMember
        fields = ("id", "first_name", "last_name", "role")


class CrewMemberListSerializer(CrewMemberSerializer):
    role = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class CrewMemberRetrieveSerializer(CrewMemberSerializer):
    role = RoleSerializer()


class CrewGroupSerializer(serializers.ModelSerializer):
    pilots = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects
        .select_related("role")
        .filter(role__name__in=("Captain", "First Officer", "Relief Pilot"))
    )
    stewards = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects
        .select_related("role")
        .filter(role__name__in=("Purser", "Lead Flight Attendant", "Flight Attendant"))
    )
    technicians = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects
        .select_related("role")
        .filter(role__name__in=("Aircraft Mechanic", "Avionics Technician"))
    )
    additional_staff = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects
        .select_related("role")
        .exclude(role__name__in=(
            "Captain",
            "First Officer",
            "Relief Pilot",
            "Purser",
            "Lead Flight Attendant",
            "Flight Attendant",
            "Aircraft Mechanic",
            "Avionics Technician"
        ))
    )

    class Meta:
        model = CrewGroup
        fields = (
            "id",
            "crew_code",
            "description",
            "pilots",
            "stewards",
            "technicians",
            "additional_staff",
        )
        read_only_fields = ("id", "description")


class CrewGroupListSerializer(CrewGroupSerializer):
    pilots = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    stewards = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    technicians = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    additional_staff = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )


class CrewGroupRetrieveSerializer(CrewGroupSerializer):
    pilots = CrewMemberListSerializer(many=True)
    stewards = CrewMemberListSerializer(many=True)
    technicians = CrewMemberListSerializer(many=True)
    additional_staff = CrewMemberListSerializer(many=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


# SeatConfiguration serializers for Airplane model (without 'airplane' field)

class SeatClassDisplayMixin(serializers.ModelSerializer):
    seats_class = serializers.CharField(
        source="get_seats_class_display",
        read_only=True
    )

class SeatConfigurationAirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatConfiguration
        fields = ("id", "seats_class", "rows", "seats_in_row")


class SeatConfigurationAirplaneListSerializer(SeatClassDisplayMixin):
    class Meta:
        model = SeatConfiguration
        fields = ("seats_class", "num_of_seats")


class SeatConfigurationAirplaneRetrieveSerializer(
    SeatConfigurationAirplaneSerializer,
    SeatClassDisplayMixin
):
    pass

# -------------------------------------------------------------------------------


class AirplaneBaseSerializer(serializers.ModelSerializer):
    seats_configuration = SeatConfigurationAirplaneSerializer(many=True)

    class Meta:
        model = Airplane
        fields = ("id", "model_name", "type", "seats_configuration")

    def create(self, validated_data) -> Airplane:
        with transaction.atomic():
            configurations_data = validated_data.pop("seats_configuration", None)
            airplane = Airplane.objects.create(**validated_data)
            SeatConfiguration.objects.bulk_create([
                SeatConfiguration(airplane=airplane, **conf)
                for conf in configurations_data
            ])

            return airplane

    def update(self, instance, validated_data) -> Airplane:
        with transaction.atomic():
            instance.model_name = validated_data.get("model_name", instance.model_name)
            instance.type = validated_data.get("type", instance.type)
            instance.save()

            configurations_data = validated_data.pop("seats_configuration", [])

            if configurations_data is not None:
                instance.seats_configuration.all().delete()
                SeatConfiguration.objects.bulk_create([
                    SeatConfiguration(airplane=instance, **conf)
                    for conf in configurations_data
                ])

            return instance

    def to_representation(self, instance) -> dict:
        data = super().to_representation(instance)

        if self.context.get("is_list_view"):
            data["seats_configuration"] = SeatConfigurationAirplaneListSerializer(
                instance.seats_configuration.all(),
                many=True
            ).data
            data["type"] = instance.type.name

        if self.context.get("is_detail_view"):
            data["seats_configuration"] = SeatConfigurationAirplaneRetrieveSerializer(
                instance.seats_configuration.all(),
                many=True
            ).data
            data["type"] = AirplaneTypeSerializer(instance.type).data

        return data


class AirplaneSeatConfigurationRetrieveSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = ("id", "model_name", "type")


#   Serializers for SeatConfiguration model (with 'airplane' field)

class SeatConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatConfiguration
        fields = ("id", "seats_class", "rows", "seats_in_row", "airplane")


class SeatConfigurationListSerializer(
    SeatConfigurationSerializer,
    SeatClassDisplayMixin
):
    airplane = serializers.SlugRelatedField(
        read_only=True,
        slug_field="model_name"
    )


class SeatConfigurationRetrieveSerializer(SeatConfigurationListSerializer):
    airplane = AirplaneSeatConfigurationRetrieveSerializer()


class SeatConfigurationFilterSerializer(serializers.ModelSerializer):
    seats_class = serializers.CharField(
        required=False,
        validators=[validate_seat_class]
    )
    airplane = serializers.CharField(required=False)

    class Meta:
        model = SeatConfiguration
        fields = ("seats_class", "airplane")

# --------------------------------------------------------------------


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "status",
            "crew"
        )


class FlightListSerializer(FlightSerializer):
    crew = serializers.SlugRelatedField(
        read_only=True,
        slug_field="crew_code"
    )
    route = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    airplane = serializers.SlugRelatedField(
        read_only=True,
        slug_field="model_name"
    )
    departure_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    arrival_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    status = serializers.CharField(
        read_only=True,
        source="get_status_display"
    )


class FlightRetrieveSerializer(FlightListSerializer):
    route = RouteListSerializer()
    airplane = AirplaneSeatConfigurationRetrieveSerializer()
    crew = CrewGroupListSerializer()


class FlightFilterSerializer(serializers.ModelSerializer):
    departure_time_after = serializers.DateField(required=False)
    departure_time_before = serializers.DateField(required=False)
    arrival_time_after = serializers.DateField(required=False)
    arrival_time_before = serializers.DateField(required=False)

    source_city = serializers.CharField(required=False)
    destination_city = serializers.CharField(required=False)

    class Meta:
        model = Flight
        fields = (
            "departure_time_after",
            "departure_time_before",
            "arrival_time_after",
            "arrival_time_before",
            "source_city",
            "destination_city",
        )

    def validate(self, data):
        if "departure_time_after" in data and "departure_time_before" in data:
            if data["departure_time_after"] > data["departure_time_before"]:
                raise serializers.ValidationError(
                    "departure_time_after must be earlier than departure_time_before."
                )

        if "arrival_time_after" in data and "arrival_time_before" in data:
            if data["arrival_time_after"] > data["arrival_time_before"]:
                raise serializers.ValidationError(
                    "arrival_time_after must be earlier than arrival_time_before."
                )

        if "source_city" in data and "destination_city" in data:
            Route.validate_source_and_destination(
                data["source_city"],
                data["destination_city"],
                serializers.ValidationError
            )

        return data


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "passenger_first_name",
            "passenger_last_name",
            "seat_class",
            "flight"
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id","created_at", "tickets")

    def create(self, validated_data) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets", None)
            order = Order.objects.create(**validated_data)
            for ticket in tickets_data:
                Ticket.objects.create(order=order, **ticket)
            return order


class TicketListSerializer(TicketSerializer):
    seat_class_ = serializers.SerializerMethodField()
    trip = serializers.CharField(
        source="flight.route.name",
        read_only=True
    )
    passenger = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            "id",
            "passenger",
            "seat_class_",
            "trip"
        )

    def get_seat_class_(self, obj):
        return obj.get_seat_class_display()

    def get_passenger(self, obj):
        return f"{obj.passenger_first_name} {obj.passenger_last_name}"


class TicketRetrieveSerializer(TicketSerializer):
    seat_class_ = serializers.SerializerMethodField()
    flight = serializers.SlugRelatedField(
        read_only=True,
        slug_field="flight_number"
    )
    source = serializers.CharField(
        read_only=True,
        source="flight.route.source"
    )
    destination = serializers.CharField(
        read_only=True,
        source="flight.route.destination"
    )
    departure_time = serializers.DateTimeField(
        format="%d %b %Y, %H:%M",
        source="flight.departure_time"
    )
    arrival_time = serializers.DateTimeField(
        format="%d %b %Y, %H:%M",
        source="flight.arrival_time"
    )

    def get_seat_class_(self, obj):
        return obj.get_seat_class_display()

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "passenger_first_name",
            "passenger_last_name",
            "seat_class_",
            "flight",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
        )


class OrderListSerializer(OrderSerializer):
    created_at = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderRetrieveSerializer(OrderListSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
