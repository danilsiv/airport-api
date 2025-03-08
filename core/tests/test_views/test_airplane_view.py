from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import Airplane
from core.serializers import AirplaneBaseSerializer
from core.tests.factories import create_airplane_type, create_airplane


AIRPLANE_URL = reverse("core:airplane-list")

def detail_url(airplane_id: int):
    return reverse("core:airplane-detail", args=[airplane_id])


class AdminAirportApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        type_1 = create_airplane_type(name="test_1")
        type_2 = create_airplane_type(name="test_2")
        self.airplane_1 = create_airplane(model_name="test_1", type=type_1)
        self.airplane_2 = create_airplane(model_name="test_2", type=type_2)

    def test_airplane_list(self) -> None:
        response = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneBaseSerializer(
            airplanes, many=True, context={"is_list_view": True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_airplanes_by_params(self) -> None:
        responses = (
            self.client.get(AIRPLANE_URL, {"model_name": self.airplane_1.model_name}),
            self.client.get(AIRPLANE_URL, {"model_type": self.airplane_1.type.name})
        )

        serializer_1 = AirplaneBaseSerializer(self.airplane_1, context={"is_list_view": True})
        serializer_2 = AirplaneBaseSerializer(self.airplane_2, context={"is_list_view": True})

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn(serializer_1.data, response.data["results"])
            self.assertNotIn(serializer_2.data, response.data["results"])

    def test_airplane_retrieve(self) -> None:
        response = self.client.get(detail_url(self.airplane_1.id))
        serializer = AirplaneBaseSerializer(self.airplane_1, context={"is_detail_view": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airplane_with_configurations(self) -> None:
        seats_conf_1 = {"seats_class": "EC", "rows": 15, "seats_in_row": 5}
        seats_conf_2 = {"seats_class": "BC", "rows": 15, "seats_in_row": 5}
        seats_conf_3 = {"seats_class": "FC", "rows": 15, "seats_in_row": 5}

        payload = create_airplane(as_dict=True)
        payload["seats_configuration"] = [seats_conf_1, seats_conf_2, seats_conf_3]

        response = self.client.post(AIRPLANE_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("seats_configuration", response.data)
        self.assertEqual(len(response.data["seats_configuration"]), 3)
