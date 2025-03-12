from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import Role
from core.serializers import RoleSerializer
from core.tests.factories import create_role


ROLE_URL = reverse("core:role-list")


class AdminRouteApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.role_1 = create_role(name="test_1")
        self.role_2 = create_role(name="test_2")

    def test_role_list(self) -> None:
        response = self.client.get(ROLE_URL)
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_role_create(self) -> None:
        payload = create_role(as_dict=True)
        response = self.client.post(ROLE_URL, payload)
        role = Role.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], role.name)
