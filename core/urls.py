from django.urls import path, include
from rest_framework import routers

from core.views import CityViewSet, AirportViewSet


router = routers.DefaultRouter()

router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "core"
