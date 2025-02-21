from django.urls import path, include
from rest_framework import routers

from core.views import (
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    RoleListView,
    CrewMemberViewSet,
    CrewGroupViewSet,
    AirplaneTypeListView,
    AirplaneViewSet,
    SeatConfigurationViewSet,
)


router = routers.DefaultRouter()

router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("crew-members", CrewMemberViewSet)
router.register("crew-groups", CrewGroupViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("seat-configurations", SeatConfigurationViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("roles/", RoleListView.as_view(), name="role_list"),
    path(
        "airplane-types/",
        AirplaneTypeListView.as_view(),
        name="airplane_type_list"
    )
]

app_name = "core"
