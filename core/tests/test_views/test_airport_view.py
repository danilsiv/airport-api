from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import Airport
from core.serializers import AirportListSerializer, AirportRetrieveSerializer
from core.tests.factories import create_city, create_airport


AIRPORT_URL = reverse("core:airport-list")

def detail_url(airport_id: int):
    return reverse("core:airport-detail", args=[airport_id])


class AdminCityApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.uk_city = create_city(country="UK")
        self.usa_city = create_city(country="USA")

        self.uk_airport = create_airport(city=self.uk_city)
        self.usa_airport = create_airport(city=self.usa_city)

    def test_airport_list(self) -> None:
        response = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_airports_by_country(self) -> None:
        response = self.client.get(AIRPORT_URL, {"country": f"{self.uk_city.country}"})
        uk_serializer = AirportListSerializer(self.uk_airport)
        usa_serializer = AirportListSerializer(self.usa_airport)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(uk_serializer.data, response.data["results"])
        self.assertNotIn(usa_serializer.data, response.data["results"])

    def test_airport_retrieve(self) -> None:
        response = self.client.get(detail_url(self.uk_airport.id))
        serializer = AirportRetrieveSerializer(self.uk_airport)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_create(self) -> None:
        payload = create_airport(as_dict=True)
        response = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], airport.name)
        self.assertEqual(response.data["iata_code"], airport.iata_code)
        self.assertEqual(response.data["city"], airport.city.id)
