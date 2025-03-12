from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import SeatConfiguration
from core.serializers import SeatConfigurationListSerializer, SeatConfigurationRetrieveSerializer
from core.tests.factories import create_airplane, create_seat_configuration

CONF_URL = reverse("core:seatconfiguration-list")

def detail_url(conf_id: int):
    return reverse("core:seatconfiguration-detail", args=[conf_id])


class AdminAirplaneApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        airplane_1 = create_airplane(model_name="test_1")
        airplane_2 = create_airplane(model_name="test_2")
        self.seat_configuration_1 = create_seat_configuration(
            seats_class="EC",
            airplane=airplane_1,
        )
        self.seat_configuration_2 = create_seat_configuration(
            seats_class="BC",
            airplane=airplane_2
        )

    def test_seat_configuration_list(self) -> None:
        response = self.client.get(CONF_URL)
        seat_configurations = SeatConfiguration.objects.all()
        serializer = SeatConfigurationListSerializer(seat_configurations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_seat_configurations_by_params(self) -> None:
        serializer_1 = SeatConfigurationListSerializer(self.seat_configuration_1)
        serializer_2 = SeatConfigurationListSerializer(self.seat_configuration_2)

        responses = (
            self.client.get(
                CONF_URL,
                {"airplane": self.seat_configuration_1.airplane.model_name}
            ),
            self.client.get(
                CONF_URL,
                {"seats_class": self.seat_configuration_1.seats_class}
            )
        )
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn(serializer_1.data, response.data["results"])
            self.assertNotIn(serializer_2.data, response.data["results"])

    def test_seat_configuration_retrieve(self) -> None:
        response = self.client.get(detail_url(self.seat_configuration_1.id))
        serializer = SeatConfigurationRetrieveSerializer(self.seat_configuration_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_seat_configuration_create(self) -> None:
        payload = create_seat_configuration(as_dict=True)
        response = self.client.post(CONF_URL, payload)
        seat_conf = SeatConfiguration.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["seats_class"], seat_conf.seats_class)
        self.assertEqual(payload["rows"], seat_conf.rows)
        self.assertEqual(payload["airplane"], seat_conf.airplane.id)