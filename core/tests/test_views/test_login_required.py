from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.tests.factories import (
    create_city,
    create_airport,
    create_route,
    create_crew_member,
    create_crew_group,
    create_airplane,
    create_seat_configuration,
    create_flight,
    create_order,
)


class UnauthenticatedAirportApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.city = create_city()
        self.airport = create_airport()
        self.route, self.route_data = create_route(as_tuple=True)
        self.crew_member = create_crew_member()
        self.crew_group = create_crew_group()
        self.airplane = create_airplane()
        self.seat_configuration = create_seat_configuration()
        self.flight = create_flight()
        self.order, self.order_data = create_order(as_tuple=True)

    def test_available_endpoints(self) -> None:

        responses = (
            self.client.get(reverse("core:city-list")),
            self.client.get(reverse("core:city-detail", args=[self.city.id])),

            self.client.get(reverse("core:airport-list")),
            self.client.get(reverse("core:airport-detail", args=[self.airport.id])),

            self.client.get(reverse("core:route-list")),
            self.client.get(reverse("core:route-detail", args=[self.route.id])),

            self.client.get(reverse("core:airplane-list")),
            self.client.get(reverse("core:airplane-detail", args=[self.airplane.id])),

            self.client.get(reverse("core:flight-list")),
            self.client.get(reverse("core:flight-detail", args=[self.flight.id])),
        )

        for response in responses:
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Unexpected status {response.status_code} for {response.request['PATH_INFO']}"
            )
