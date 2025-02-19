from django.db.models import QuerySet
from rest_framework import viewsets


from core.models import City, Airport, Route
from core.serializers import (
    CitySerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportRetrieveSerializer

        return AirportSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(city__name__icontains=country)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("city")

        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer

        return RouteSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "source__city", "destination__city"
            )

        return queryset
