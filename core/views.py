from django.db.models import QuerySet
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework import generics

from core.models import (
    City,
    Airport,
    Route,
    Role,
    CrewMember,
    CrewGroup,
    AirplaneType,
    Airplane,
    SeatConfiguration, Flight,
)
from core.serializers import (
    CitySerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    RoleSerializer,
    CrewMemberSerializer,
    CrewMemberListSerializer,
    CrewMemberRetrieveSerializer,
    CrewGroupSerializer,
    CrewGroupListSerializer,
    CrewGroupRetrieveSerializer,
    AirplaneTypeSerializer,
    SeatConfigurationSerializer,
    SeatConfigurationListSerializer,
    SeatConfigurationRetrieveSerializer,
    SeatConfigurationFilterSerializer,
    AirplaneBaseSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
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

        return self.serializer_class

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

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        source_name = self.request.query_params.get("source_name")
        if source_name:
            queryset = queryset.filter(source__name=source_name)

        destination_name = self.request.query_params.get("destination_name")
        if destination_name:
            queryset = queryset.filter(destination__name=destination_name)

        source_iata = self.request.query_params.get("source_iata")
        if source_iata:
            queryset = queryset.filter(source__iata_code=source_iata)

        destination_iata = self.request.query_params.get("destination_iata")
        if destination_iata:
            queryset = queryset.filter(destination__iata_code=destination_iata)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "source__city", "destination__city"
            )

        return queryset


class RoleListView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class CrewMemberViewSet(viewsets.ModelViewSet):
    queryset = CrewMember.objects.all()
    serializer_class = CrewMemberSerializer

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return CrewMemberListSerializer
        if self.action == "retrieve":
            return CrewMemberRetrieveSerializer

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role__name__icontains=role)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("role")

        return queryset


class CrewGroupViewSet(viewsets.ModelViewSet):
    queryset = CrewGroup.objects.all()
    serializer_class = CrewGroupSerializer

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return CrewGroupListSerializer
        if self.action == "retrieve":
            return CrewGroupRetrieveSerializer

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        if self.action in ("retrieve", "list"):
            return self.queryset.select_related("flight").prefetch_related(
                "pilots__role",
                "stewards__role",
                "technicians__role",
                "additional_staff__role",
            )
        return self.queryset


class AirplaneTypeListView(generics.ListCreateAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneBaseSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        model_name = self.request.query_params.get("name")
        if model_name:
            queryset = queryset.filter(model_name__icontains=model_name)

        model_type = self.request.query_params.get("type")
        if model_type:
            queryset = queryset.filter(type__name__icontains=model_type)

        if self.action in ("list", "retrieve"):
            return queryset.select_related().prefetch_related("seats_configuration")

        return queryset

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context["is_list_view"] = self.action == "list"
        context["is_detail_view"] = self.action == "retrieve"
        return context


class SeatConfigurationViewSet(viewsets.ModelViewSet):
    queryset = SeatConfiguration.objects.all()
    serializer_class = SeatConfigurationSerializer

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return SeatConfigurationListSerializer
        if self.action == "retrieve":
            return SeatConfigurationRetrieveSerializer

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        filter_serializer = SeatConfigurationFilterSerializer(
            data=self.request.query_params
        )
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        if "airplane" in filters:
            queryset = queryset.filter(airplane__model_name=filters["airplane"])

        if "seats_class" in filters:
            queryset = queryset.filter(seats_class=filters["seats_class"])

        if self.action in ("list", "retrieve"):
            return queryset.select_related()

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        departure_after = self.request.query_params.get("departure_time_after")
        departure_before = self.request.query_params.get("departure_time_before")
        arrival_after = self.request.query_params.get("arrival_time_after")
        arrival_before = self.request.query_params.get("arrival_time_before")

        if departure_after:
            # TODO: validation
            queryset = queryset.filter(
                departure_time__gte=parse_date(departure_after)
            )
        if departure_before:
            # TODO: validation
            queryset = queryset.filter(
                departure_time__lte=parse_date(departure_before)
            )
        if arrival_after:
            # TODO: validation
            queryset = queryset.filter(
                arrival_time__gte=parse_date(arrival_after)
            )
        if arrival_before:
            # TODO: validation
            queryset = queryset.filter(
                arrival_time__lte=parse_date(arrival_before)
            )

        if self.action == "list":
            queryset = queryset.select_related(
                "route__destination__city",
                "route__source__city",
                "airplane"
            )
        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__destination__city",
                "route__source__city",
                "airplane__type",
                "crew"
            )

        return queryset
