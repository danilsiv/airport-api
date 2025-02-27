from django.db.models import QuerySet, F, Count, Q, Case, When, Value, IntegerField, Sum
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import mixins

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
    Flight,
    Order,
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
    FlightFilterSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
)
from core.pagination import CityRolePagination, FlightOrderPagination


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = CityRolePagination


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

        route_code = self.request.query_params.get("route_code")
        if route_code:
            queryset = queryset.filter(route_code=route_code)

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
    pagination_class = CityRolePagination


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
    pagination_class = FlightOrderPagination

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        filter_serializer = FlightFilterSerializer(
            data=self.request.query_params
        )
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        if "departure_time_after" in filters:
            queryset = queryset.filter(
                departure_time__gte=filters["departure_time_after"]
            )
        if "departure_time_before" in filters:
            queryset = queryset.filter(
                departure_time__lte=filters["departure_time_before"]
            )
        if "arrival_time_after" in filters:
            queryset = queryset.filter(
                arrival_time__gte=filters["arrival_time_after"]
            )
        if "arrival_time_before" in filters:
            queryset = queryset.filter(
                arrival_time__lte=filters["arrival_time_before"]
            )

        if "source_city" in filters:
            queryset = queryset.filter(
                route__source__city__name=filters["source_city"]
            )
        if "destination_city" in filters:
            queryset = queryset.filter(
                route__destination__city__name=filters["destination_city"]
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "route__destination__city",
                "route__source__city",
                "airplane__type",
                "crew"
            ).annotate(
                ec_total=Sum(
                    Case(
                    When(airplane__seats_configuration__seats_class="EC",
                         then=F("airplane__seats_configuration__seats_in_row")
                              * F("airplane__seats_configuration__rows")
                         ),
                    default=Value(0),
                    output_field=IntegerField()
                )),
                bc_total=Sum(
                    Case(
                    When(airplane__seats_configuration__seats_class="BC",
                         then=F("airplane__seats_configuration__seats_in_row")
                              * F("airplane__seats_configuration__rows")
                         ),
                    default=Value(0),
                    output_field=IntegerField()
                )),
                fc_total=Sum(
                    Case(
                    When(airplane__seats_configuration__seats_class="FC",
                         then=F("airplane__seats_configuration__seats_in_row")
                              * F("airplane__seats_configuration__rows")
                         ),
                    default=Value(0),
                    output_field=IntegerField()
                )),
                ec_booked=Count("tickets", filter=Q(tickets__seat_class="EC")),
                bc_booked=Count("tickets", filter=Q(tickets__seat_class="BC")),
                fc_booked=Count("tickets", filter=Q(tickets__seat_class="FC")),
                ec_available=F("ec_total") - F("ec_booked"),
                bc_available=F("bc_total") - F("bc_booked"),
                fc_available=F("fc_total") - F("fc_booked")
            )

        return queryset


class OrderListCreateRetrieveView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = FlightOrderPagination

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderRetrieveSerializer

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset.filter(user=self.request.user)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "tickets__flight__route__source__city",
                "tickets__flight__route__destination__city"
            )

        return queryset
