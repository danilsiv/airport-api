from rest_framework import serializers

from core.validators import validate_iata_code_format
from core.models import City, Airport, Route


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "iata_code", "city")
        validators = [validate_iata_code_format]


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


class RouteListSerializer(RouteSerializer):
    source = AirportListSerializer()
    destination = AirportListSerializer()


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportRetrieveSerializer()
    destination = AirportRetrieveSerializer()
