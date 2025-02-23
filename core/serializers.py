from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
            ValidationError
        )


class RouteListSerializer(RouteSerializer):
    source = AirportListSerializer()
    destination = AirportListSerializer()


class RouteRetrieveSerializer(RouteSerializer):
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

class SeatConfigurationAirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatConfiguration
        fields = ("id", "seats_class", "rows", "seats_in_row")


class SeatConfigurationAirplaneListSerializer(serializers.ModelSerializer):
    seats_class = serializers.CharField(
        source="get_seats_class_display",
        read_only=True
    )

    class Meta:
        model = SeatConfiguration
        fields = ("seats_class", "num_of_seats")


class SeatConfigurationAirplaneRetrieveSerializer(SeatConfigurationAirplaneSerializer):
    seats_class = serializers.CharField(
        source="get_seats_class_display",
        read_only=True
    )

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


class SeatConfigurationListSerializer(SeatConfigurationSerializer):
    seats_class = serializers.CharField(
        source="get_seats_class_display",
        read_only=True
    )
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
