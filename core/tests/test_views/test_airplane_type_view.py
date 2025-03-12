from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import AirplaneType
from core.serializers import AirplaneTypeSerializer
from core.tests.factories import create_airplane_type


TYPE_URL = reverse("core:airplane-type-list")


class AdminAirplaneTypeApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_airplane_type_list(self) -> None:
        create_airplane_type(name="test_1")
        create_airplane_type(name="test_2")

        response = self.client.get(TYPE_URL)
        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_type_create(self) -> None:
        payload = create_airplane_type(as_dict=True)
        response = self.client.post(TYPE_URL, payload)
        airplane_type = AirplaneType.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], airplane_type.name)
