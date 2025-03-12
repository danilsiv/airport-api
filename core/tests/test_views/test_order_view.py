from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import Order
from core.serializers import OrderListSerializer, OrderRetrieveSerializer
from core.tests.factories import create_ticket, create_airplane, create_flight, create_crew_group

ORDER_URL = reverse("core:order-list")

def detail_url(order_id: int):
    return reverse("core:order-detail", args=[order_id])


class AdminOrderApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_order_list_create_retrieve(self) -> None:
        airplane = create_airplane(model_name="test")
        crew = create_crew_group(crew_code="ABCD")
        flight = create_flight(flight_number="AA4321", crew=crew, airplane=airplane)

        ticket_1 = create_ticket(as_dict=True, seat=1, airplane=airplane, flight=flight)
        ticket_2 = create_ticket(as_dict=True, seat=2, airplane=airplane, flight=flight)
        ticket_3 = create_ticket(as_dict=True, seat=3, airplane=airplane, flight=flight)
        ticket_4 = create_ticket(as_dict=True, seat=4, airplane=airplane, flight=flight)

        order_1 = {"tickets": [ticket_1, ticket_2]}
        order_2 = {"tickets": [ticket_3, ticket_4]}

        response_1 = self.client.post(ORDER_URL, order_1, format="json")
        response_2 = self.client.post(ORDER_URL, order_2, format="json")

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response_1.data["tickets"]), len(order_1["tickets"]))
        self.assertEqual(len(response_2.data["tickets"]), len(order_2["tickets"]))

        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)
        response = self.client.get(ORDER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        order = Order.objects.get(id=response_1.data["id"])
        response = self.client.get(detail_url(order.id))
        serializer = OrderRetrieveSerializer(order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
