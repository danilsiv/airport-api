from django.urls import path, include
from rest_framework import routers

from core.views import (
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    RoleListView,
)


router = routers.DefaultRouter()

router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("roles/", RoleListView.as_view(), name="role_list"),
]

app_name = "core"
