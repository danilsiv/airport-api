from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import Route
from core.serializers import RouteListSerializer, RouteRetrieveSerializer, RouteSerializer
from core.tests.factories import create_airport, create_route


ROUTE_URL = reverse("core:route-list")

def detail_url(route_id: int):
    return reverse("core:route-detail", args=[route_id])


class AdminRouteApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airport_1 = create_airport(name="test_1", iata_code="AAA")
        self.airport_2 = create_airport(name="test_2", iata_code="BBB")

        self.route_1 = create_route(source=self.airport_1, destination=self.airport_2)
        self.route_2 = create_route(source=self.airport_2, destination=self.airport_1)

        self.serializer_1 = RouteListSerializer(self.route_1)
        self.serializer_2 = RouteListSerializer(self.route_2)

    def test_route_list(self) -> None:
        response = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_routes_by_route_code(self) -> None:
        response = self.client.get(ROUTE_URL, {"route_code": self.route_1.route_code})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, response.data["results"])
        self.assertNotIn(self.serializer_2.data, response.data["results"])

    def test_filter_routes_by_source_name(self) -> None:
        response = self.client.get(ROUTE_URL, {"source_name": self.route_1.source.name})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, response.data["results"])
        self.assertNotIn(self.serializer_2.data, response.data["results"])

    def test_filter_routes_by_destination_name(self) -> None:
        response = self.client.get(
            ROUTE_URL, {"destination_name": self.route_1.destination.name}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, response.data["results"])
        self.assertNotIn(self.serializer_2.data, response.data["results"])

    def test_filter_routes_by_source_iata_code(self) -> None:
        response = self.client.get(
            ROUTE_URL, {"source_iata": self.route_1.source.iata_code}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, response.data["results"])
        self.assertNotIn(self.serializer_2.data, response.data["results"])

    def test_filter_routes_by_destination_iata_code(self) -> None:
        response = self.client.get(
            ROUTE_URL, {"destination_iata": self.route_1.destination.iata_code}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, response.data["results"])
        self.assertNotIn(self.serializer_2.data, response.data["results"])

    def test_route_retrieve(self) -> None:
        response = self.client.get(detail_url(self.route_1.id))
        serializer = RouteRetrieveSerializer(self.route_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_route_create(self) -> None:
        payload = {
            "source": create_airport().id,
            "destination": create_airport().id,
            "distance": 5000
        }
        response = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["source"], route.source.id)
        self.assertEqual(payload["destination"], route.destination.id)
        self.assertEqual(payload["distance"], route.distance)
