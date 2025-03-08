from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import CrewGroup
from core.serializers import CrewGroupListSerializer, CrewGroupRetrieveSerializer
from core.tests.factories import create_crew_group, create_crew_member, create_role

CREW_URL = reverse("core:crewgroup-list")

def detail_url(crew_id: int):
    return reverse("core:crewgroup-detail", args=[crew_id])


class AdminCrewGroupApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.crew_group_1 = create_crew_group(crew_code="test1")
        self.crew_group_2 = create_crew_group(crew_code="test2")

    def test_crew_group_list(self) -> None:
        response = self.client.get(CREW_URL)
        crew_groups = CrewGroup.objects.all()
        serializer = CrewGroupListSerializer(crew_groups, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_crew_group_retrieve(self) -> None:
        response = self.client.get(detail_url(self.crew_group_1.id))
        serializer = CrewGroupRetrieveSerializer(self.crew_group_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_crew_group_with_members(self) -> None:
        pilot_role = create_role(name="Captain")
        steward_role = create_role(name="Purser")
        tech_role = create_role(name="Aircraft Mechanic")
        add_role = create_role(name="Additional")

        pilot = create_crew_member(role=pilot_role)
        steward = create_crew_member(role=steward_role)
        technician = create_crew_member(role=tech_role)
        additional_staff = create_crew_member(role=add_role)

        payload = create_crew_group(as_dict=True)
        payload["pilots"] = [pilot.id]
        payload["stewards"] = [steward.id]
        payload["technicians"] = [technician.id]
        payload["additional_staff"] = [additional_staff.id]
        response = self.client.post(CREW_URL, payload)
        crew_group = CrewGroup.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["crew_code"], crew_group.crew_code)
        self.assertIn(pilot, crew_group.pilots.all())
        self.assertIn(steward, crew_group.stewards.all())
        self.assertIn(technician, crew_group.technicians.all())
        self.assertIn(additional_staff, crew_group.additional_staff.all())
