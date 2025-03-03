from django.db.models import QuerySet, F, Count, Q, Case, When, Value, IntegerField, Sum
from rest_framework import viewsets, status
from rest_framework import generics
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from core.models import (
    SEATS_CLASS_CHOICES,
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
    CrewMemberPhotoSerializer,
)
from core.pagination import CityRolePagination, FlightOrderPagination
from core.permissions import IsAdminUserOrReadOnly


@extend_schema_view(
    create=extend_schema(summary="Create city"),
    list=extend_schema(summary="List cities"),
    retrieve=extend_schema(summary="Get city details"),
    update=extend_schema(summary="Update city"),
    partial_update=extend_schema(summary="Partially update city"),
    destroy=extend_schema(summary="Delete city"),
)
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = CityRolePagination
    permission_classes = (IsAdminUserOrReadOnly,)


@extend_schema_view(
    create=extend_schema(summary="Create airport"),
    retrieve=extend_schema(summary="Get airport details"),
    update=extend_schema(summary="Update airport"),
    partial_update=extend_schema(summary="Partially update airport"),
    destroy=extend_schema(summary="Delete airport"),
)
class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

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
            queryset = queryset.filter(city__country__icontains=country)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("city")

        return queryset

    @extend_schema(
        summary="List airports",
        description="Returns a list of airports with optional country filter.",
        parameters=[
            OpenApiParameter(
                name="country",
                type=OpenApiTypes.STR,
                description="Filter by country.",
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(summary="Create route"),
    retrieve=extend_schema(summary="Get route details"),
    update=extend_schema(summary="Update route"),
    partial_update=extend_schema(summary="Partially update route"),
    destroy=extend_schema(summary="Delete route"),
)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

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

    @extend_schema(
        summary="List routes",
        description="Returns a list of routes with optional filter params.",
        parameters=[
            OpenApiParameter(
                name="route_code",
                type=OpenApiTypes.STR,
                description="Filter by route using IATA codes in the format 'SOURCE-DESTINATION'. "
                            "Example: 'JFK-LHR'.",
                required=False
            ),
            OpenApiParameter(
                name="source_name",
                type=OpenApiTypes.STR,
                description="Filter by name of source.",
                required=False
            ),
            OpenApiParameter(
                name="destination_name",
                type=OpenApiTypes.STR,
                description="Filter by name of destination.",
                required=False
            ),
            OpenApiParameter(
                name="source_iata",
                type=OpenApiTypes.STR,
                description="Filter by IATA of source.",
                required=False
            ),
            OpenApiParameter(
                name="destination_iata",
                type=OpenApiTypes.STR,
                description="Filter by IATA of destination.",
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(summary="List roles"),
    create=extend_schema(summary="Create role")
)
class RoleListView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = CityRolePagination


@extend_schema_view(
    create=extend_schema(summary="Create crew member"),
    retrieve=extend_schema(summary="Get crew member details"),
    update=extend_schema(summary="Update crew member"),
    partial_update=extend_schema(summary="Partially update crew member"),
    destroy=extend_schema(summary="Delete crew member"),
    upload_photo=extend_schema(summary="Upload crew member photo")
)
class CrewMemberViewSet(viewsets.ModelViewSet):
    queryset = CrewMember.objects.all()
    serializer_class = CrewMemberSerializer

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return CrewMemberListSerializer
        if self.action == "retrieve":
            return CrewMemberRetrieveSerializer
        if self.action == "upload_photo":
            return CrewMemberPhotoSerializer

        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role__name__icontains=role)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("role")

        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-photo"
    )
    def upload_photo(self, request, pk=None):
        crew_member = self.get_object()
        serializer = self.get_serializer(crew_member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="List crew members",
        description="Returns a list of crew members with optional role filter.",
        parameters=[
            OpenApiParameter(
                name="role",
                type=OpenApiTypes.STR,
                description="Filter by role of crew member.",
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(summary="Create crew croup"),
    list=extend_schema(summary="List crew groups"),
    retrieve=extend_schema(summary="Get crew group details"),
    update=extend_schema(summary="Update crew group"),
    partial_update=extend_schema(summary="Partially update crew group"),
    destroy=extend_schema(summary="Delete crew group"),
)
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


@extend_schema_view(
    create=extend_schema(summary="Create airplane type"),
    list=extend_schema(summary="List airplane types")
)
class AirplaneTypeListView(generics.ListCreateAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


@extend_schema_view(
    create=extend_schema(summary="Create airplane"),
    retrieve=extend_schema(summary="Get airplane details"),
    update=extend_schema(summary="Update airplane"),
    partial_update=extend_schema(summary="Partially update airplane"),
    destroy=extend_schema(summary="Delete airplane"),
)
class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneBaseSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        model_name = self.request.query_params.get("model_name")
        if model_name:
            queryset = queryset.filter(model_name__icontains=model_name)

        model_type = self.request.query_params.get("model_type")
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

    @extend_schema(
        summary="List airplanes",
        description="Returns a list of airplanes with optional filter params.",
        parameters=[
            OpenApiParameter(
                name="model_name",
                type=OpenApiTypes.STR,
                description="Filter by model name of airplane.",
                required=False
            ),
            OpenApiParameter(
                name="model_type",
                type=OpenApiTypes.STR,
                description="Filter by type of airplane.",
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(summary="Create seat configuration"),
    retrieve=extend_schema(summary="Get seat configuration details"),
    update=extend_schema(summary="Update seat configuration"),
    partial_update=extend_schema(summary="Partially update seat configuration"),
    destroy=extend_schema(summary="Delete seat configuration"),
)
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

    @extend_schema(
        summary="List seat configurations",
        description="Returns a list of seat configurations with optional filter params.",
        parameters=[
            OpenApiParameter(
                name="airplane",
                type=OpenApiTypes.STR,
                description="Filter configurations by airplane.",
                required=False
            ),
            OpenApiParameter(
                name="seats_class",
                type=OpenApiTypes.STR,
                description="Filter by seat class. Available options: "
                            f"{', '.join([f'{db} ({dp})' for db, dp in SEATS_CLASS_CHOICES])}.",
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    pagination_class = FlightOrderPagination
    permission_classes = (IsAdminUserOrReadOnly,)

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
    permission_classes = (IsAuthenticated,)

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
