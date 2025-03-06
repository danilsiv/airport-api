from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.tests.factories import (
    create_city,
    create_airport,
    create_route,
    create_role,
    create_crew_member,
    create_crew_group,
    create_airplane_type,
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

    def test_unavailable_endpoints(self) -> None:
        city_data = create_city(as_dict=True)
        airport_data = create_airport(as_dict=True)
        member_data = create_crew_member(as_dict=True)
        crew_group_data = create_crew_group(as_dict=True)
        airplane_type_data = create_airplane_type(as_dict=True)
        airplane_data = create_airplane(as_dict=True)
        conf_data = create_seat_configuration(as_dict=True)
        flight_data = create_flight(as_dict=True)

        responses = (
            self.client.post(reverse("core:city-list"), city_data),
            self.client.put(reverse("core:city-detail", args=[self.city.id]), city_data),
            self.client.patch(reverse("core:city-detail", args=[self.city.id]), city_data),
            self.client.delete(reverse("core:city-detail", args=[self.city.id])),

            self.client.post(reverse("core:airport-list"), airport_data),
            self.client.put(reverse("core:airport-detail", args=[self.airport.id]), airport_data),
            self.client.patch(reverse("core:airport-detail", args=[self.airport.id]), airport_data),
            self.client.delete(reverse("core:airport-detail", args=[self.airport.id])),

            self.client.post(reverse("core:route-list"), self.route_data),
            self.client.put(reverse("core:route-detail", args=[self.route.id]), self.route_data),
            self.client.patch(reverse("core:route-detail", args=[self.route.id]), self.route_data),
            self.client.delete(reverse("core:route-detail", args=[self.route.id])),

            self.client.get(reverse("core:role-list")),
            self.client.post(reverse("core:role-list"), create_role(as_dict=True)),

            self.client.get(reverse("core:crewmember-list")),
            self.client.get(reverse("core:crewmember-detail", args=[self.crew_member.id])),
            self.client.post(reverse("core:crewmember-list"), member_data),
            self.client.put(reverse("core:crewmember-detail", args=[self.crew_member.id]), member_data),
            self.client.patch(reverse("core:crewmember-detail", args=[self.crew_member.id]), member_data),
            self.client.delete(reverse("core:crewmember-detail", args=[self.crew_member.id])),

            self.client.get(reverse("core:crewgroup-list")),
            self.client.get(reverse("core:crewgroup-detail", args=[self.crew_group.id])),
            self.client.post(reverse("core:crewgroup-list"), crew_group_data),
            self.client.put(reverse("core:crewgroup-detail", args=[self.crew_group.id]), crew_group_data),
            self.client.patch(reverse("core:crewgroup-detail", args=[self.crew_group.id]), crew_group_data),
            self.client.delete(reverse("core:crewgroup-detail", args=[self.crew_group.id]), crew_group_data),

            self.client.get(reverse("core:airplane-type-list")),
            self.client.post(reverse("core:airplane-type-list"), airplane_type_data),

            self.client.post(reverse("core:airplane-list"), airplane_data),
            self.client.put(reverse("core:airplane-detail", args=[self.airplane.id]), airplane_data),
            self.client.patch(reverse("core:airport-detail", args=[self.airplane.id]), airplane_data),
            self.client.delete(reverse("core:airport-detail", args=[self.airplane.id])),

            self.client.get(reverse("core:seatconfiguration-list")),
            self.client.get(reverse("core:seatconfiguration-detail", args=[self.seat_configuration.id])),
            self.client.post(reverse("core:seatconfiguration-list"), conf_data),
            self.client.put(reverse("core:seatconfiguration-detail", args=[self.seat_configuration.id]), conf_data),
            self.client.patch(reverse("core:seatconfiguration-detail", args=[self.seat_configuration.id]), conf_data),
            self.client.delete(reverse("core:seatconfiguration-detail", args=[self.seat_configuration.id])),

            self.client.post(reverse("core:flight-list"), flight_data),
            self.client.put(reverse("core:flight-detail", args=[self.flight.id]), flight_data),
            self.client.patch(reverse("core:flight-detail", args=[self.flight.id]), flight_data),
            self.client.delete(reverse("core:flight-detail", args=[self.flight.id])),

            self.client.get(reverse("core:order-list")),
            self.client.get(reverse("core:order-detail", args=[self.order.id])),
            self.client.post(reverse("core:order-list"), self.order_data),
        )
        for response in responses:
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Unexpected status {response.status_code} for {response.request['PATH_INFO']}"
            )
