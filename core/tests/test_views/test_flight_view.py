from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.tests.factories import create_flight, create_airport, create_city, create_route, create_crew_group

FLIGHT_URL = reverse("core:flight-list")

def detail_url(flight_id: int):
    return reverse("core:flight-detail", args=[flight_id])


class AdminFlightApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        source_1 = create_airport(city=create_city(name="test_1"))
        source_2 = create_airport(city=create_city(name="test_2"))
        destination_1 = create_airport(city=create_city(name="test_3"))
        destination_2 = create_airport(city=create_city(name="test_4"))

        route_1 = create_route(source=source_1, destination=destination_1)
        route_2 = create_route(source=source_2, destination=destination_2)

        crew_group_1 = create_crew_group(crew_code="ABCD")
        crew_group_2 = create_crew_group(crew_code="abcd")

        self.flight_1 = create_flight(
            flight_number="AA1111",
            route=route_1,
            departure_time="2020-02-02 02:02:00",
            arrival_time="2020-02-04 02:02:00",
            crew=crew_group_1
        )
        self.flight_2 = create_flight(
            flight_number="BB2222",
            route=route_2,
            departure_time="2022-02-02 02:02:00",
            arrival_time="2022-02-04 02:02:00",
            crew=crew_group_2
        )

        self.expected_data_1 = {
            "id": self.flight_1.id,
            "flight_number": self.flight_1.flight_number,
            "ec_available": 0,
            "bc_available": 0,
            "fc_available": 0,
            "route": self.flight_1.route.name,
            "airplane": self.flight_1.airplane.model_name,
            "departure_time": "02 Feb 2020, 02:02",
            "arrival_time": "04 Feb 2020, 02:02",
            "status": self.flight_1.get_status_display(),
            "crew": self.flight_1.crew.crew_code
        }
        self.expected_data_2 = {
            "id": self.flight_2.id,
            "flight_number": self.flight_2.flight_number,
            "ec_available": 0,
            "bc_available": 0,
            "fc_available": 0,
            "route": self.flight_2.route.name,
            "airplane": self.flight_2.airplane.model_name,
            "departure_time": "02 Feb 2022, 02:02",
            "arrival_time": "04 Feb 2022, 02:02",
            "status": self.flight_2.get_status_display(),
            "crew": self.flight_2.crew.crew_code
        }

    def test_flight_list(self) -> None:
        response = self.client.get(FLIGHT_URL)
        expected_data = [self.expected_data_1, self.expected_data_2]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"], expected_data)

    def test_filter_by_params(self) -> None:

        responses = [
            self.client.get(
                FLIGHT_URL,
                {
                    "departure_time_after": "2020-02-01",
                    "departure_time_before": "2020-02-03"
                }
            ),
            self.client.get(
                FLIGHT_URL,
                {
                    "arrival_time_after": "2020-02-03",
                    "arrival_time_before": "2020-02-05"}
            ),
            self.client.get(
                FLIGHT_URL, {
                    "source_city": self.flight_1.route.source.city.name
                }
            ),
            self.client.get(
                FLIGHT_URL, {
                    "destination_city": self.flight_1.route.destination.city.name
                }
            )
        ]

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn(self.expected_data_1, response.data["results"])
            self.assertNotIn(self.expected_data_2, response.data["results"])
