from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import (
    City,
    Airport,
    Route,
    Role,
    CrewMember,
    CrewGroup,
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
        queryset=CrewMember.objects.filter(role__name="Pilot")
    )
    stewards = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects.filter(role__name="Steward")
    )
    technicians = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects.filter(role__name="Technician")
    )
    additional_staff = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects.none()
    )

    class Meta:
        model = CrewGroup
        fields = ("id", "__str__", "pilots", "stewards", "technicians", "additional_staff")
