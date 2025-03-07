from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import City
from core.serializers import CitySerializer
from core.tests.factories import create_city


CITY_URL = reverse("core:city-list")

def detail_url(city_id: int):
    return reverse("core:city-detail", args=[city_id])


class AdminCityApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.city_1 = create_city()
        self.city_2 = create_city()

    def test_city_list(self) -> None:
        response = self.client.get(CITY_URL)
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_city_retrieve(self) -> None:
        response = self.client.get(detail_url(self.city_1.id))
        serializer = CitySerializer(self.city_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_city_create(self) -> None:
        payload = create_city(as_dict=True)
        response = self.client.post(CITY_URL, payload)
        city = City.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in payload:
            self.assertEqual(getattr(city, field), payload[field])
