from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
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


class BaseAuthAirportApiTest(TestCase):
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

    def generate_responses(
            self, view_name: str,
            instance_id: int = None,
            instance_data: dict = None,
            action_list: list[str] = None
    ) -> list[Response]:
        if not action_list:
            action_list = ["get", "retrieve", "post", "put", "patch", "delete"]

        responses = []

        if "get" in action_list:
            responses.append(self.client.get(reverse(f"core:{view_name}-list")))
        if "post" in action_list:
            responses.append(self.client.post(reverse(f"core:{view_name}-list"), instance_data))

        if instance_id:
            if "retrieve" in action_list:
                responses.append(self.client.get(
                    reverse(f"core:{view_name}-detail", args=[instance_id])
                ))
            if "put" in action_list:
                responses.append(self.client.put(
                    reverse(f"core:{view_name}-detail", args=[instance_id]), instance_data
                ))
            if "patch" in action_list:
                responses.append(self.client.patch(
                    reverse(f"core:{view_name}-detail", args=[instance_id]), instance_data
                ))
            if "delete" in action_list:
                responses.append(self.client.delete(
                    reverse(f"core:{view_name}-detail", args=[instance_id])
                ))

        return responses


class UnauthenticatedAirportApiTest(BaseAuthAirportApiTest):
    def test_available_endpoints(self) -> None:
        read_only_actions = ["get", "retrieve"]

        responses = sum([
            self.generate_responses("city", self.city.id, action_list=read_only_actions),
            self.generate_responses("airport", self.airport.id, action_list=read_only_actions),
            self.generate_responses("route", self.route.id, action_list=read_only_actions),
            self.generate_responses("airplane", self.airplane.id, action_list=read_only_actions),
            self.generate_responses("flight", self.flight.id, action_list=read_only_actions),
        ], [])

        for response in responses:
            self.assertEqual(
                response.status_code, status.HTTP_200_OK,
                f"Unexpected status {response.status_code} for {response.request['PATH_INFO']}"
            )

    def test_unavailable_endpoints(self) -> None:
        write_actions = ["post", "put", "patch", "delete"]

        responses = sum([
            self.generate_responses(
                "city", self.city.id, create_city(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "airport", self.airport.id, create_airport(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "route", self.route, self.route_data, action_list=write_actions
            ),
            self.generate_responses(
                "airplane", self.airplane.id, create_airplane(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "flight", self.flight.id, create_flight(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "crewmember", self.crew_member.id, create_crew_member(as_dict=True)
            ),
            self.generate_responses(
                "crewgroup", self.crew_group.id, create_crew_group(as_dict=True)
            ),
            self.generate_responses(
                "seatconfiguration",
                self.seat_configuration.id,
                create_seat_configuration(as_dict=True)
            ),
            self.generate_responses(
                "role", instance_data=create_role(as_dict=True), action_list=["get", "post"]
            ),
            self.generate_responses(
                "airplane-type",
                instance_data=create_airplane_type(as_dict=True),
                action_list=["get", "post"]
            ),
            self.generate_responses(
                "order", self.order.id, self.order_data, action_list=["get", "retrieve", "post"]
            ),
        ], [])

        for response in responses:
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED,
                f"Unexpected status {response.status_code} for {response.request['PATH_INFO']}"
            )


class AuthenticatedUserAirportApiTest(UnauthenticatedAirportApiTest):
    def setUp(self) -> None:
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="test123user"
        )
        self.order = create_order(user=self.user)
        self.client.force_authenticate(self.user)

    def test_available_endpoints(self) -> None:
        super().test_available_endpoints()

        order_list = self.client.get(reverse("core:order-list"))
        order_retrieve = self.client.get(reverse(f"core:order-detail", args=[self.order.id]))
        self.assertEqual(
            order_list.status_code, status.HTTP_200_OK,
            f"Unexpected status {order_list.status_code} for {order_list.request['PATH_INFO']}"
        )
        self.assertEqual(
            order_retrieve.status_code, status.HTTP_200_OK,
            f"Unexpected status {order_retrieve.status_code} for {order_retrieve.request['PATH_INFO']}"
        )

    def test_unavailable_endpoints(self) -> None:
        write_actions = ["post", "put", "patch", "delete"]

        responses = sum([
            self.generate_responses(
                "city", self.city.id, create_city(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "airport", self.airport.id, create_airport(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "route", self.route, self.route_data, action_list=write_actions
            ),
            self.generate_responses(
                "airplane", self.airplane.id, create_airplane(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "flight", self.flight.id, create_flight(as_dict=True), action_list=write_actions
            ),
            self.generate_responses(
                "crewmember", self.crew_member.id, create_crew_member(as_dict=True)
            ),
            self.generate_responses(
                "crewgroup", self.crew_group.id, create_crew_group(as_dict=True)
            ),
            self.generate_responses(
                "seatconfiguration",
                self.seat_configuration.id,
                create_seat_configuration(as_dict=True)
            ),
            self.generate_responses(
                "role", instance_data=create_role(as_dict=True), action_list=["get", "post"]
            ),
            self.generate_responses(
                "airplane-type",
                instance_data=create_airplane_type(as_dict=True),
                action_list=["get", "post"]
            )
        ], [])

        for response in responses:
            self.assertEqual(
                response.status_code, status.HTTP_403_FORBIDDEN,
                f"Unexpected status {response.status_code} for {response.request['PATH_INFO']}"
            )
