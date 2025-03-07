import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from core.models import CrewMember
from core.serializers import CrewMemberListSerializer, CrewMemberRetrieveSerializer
from core.tests.factories import create_crew_member, create_role


CREW_MEMBER_URL = reverse("core:crewmember-list")

def detail_url(member_id: int):
    return reverse("core:crewmember-detail", args=[member_id])


def photo_upload_url(member_id: int):
    return reverse("core:crewmember-upload-photo", args=[member_id])


class AdminCrewMemberApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.role_1 = create_role(name="test_1")
        self.role_2 = create_role(name="test_2")

        self.member_1 = create_crew_member(role=self.role_1)
        self.member_2 = create_crew_member(role=self.role_2)

    def test_crew_member_list(self) -> None:
        response = self.client.get(CREW_MEMBER_URL)
        members = CrewMember.objects.all()
        serializer = CrewMemberListSerializer(members, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_members_by_role(self) -> None:
        response = self.client.get(CREW_MEMBER_URL, {"role": self.member_1.role.name})
        serializer_1 = CrewMemberListSerializer(self.member_1)
        serializer_2 = CrewMemberListSerializer(self.member_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_crew_member_retrieve(self) -> None:
        response = self.client.get(detail_url(self.member_1.id))
        serializer = CrewMemberRetrieveSerializer(self.member_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_crew_member_create(self) -> None:
        payload = create_crew_member(as_dict=True)
        response = self.client.post(CREW_MEMBER_URL, payload)
        crew_member = CrewMember.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["first_name"], crew_member.first_name)
        self.assertEqual(payload["last_name"], crew_member.last_name)
        self.assertEqual(payload["role"], crew_member.role.id)


class CrewMemberPhotoUploadTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.role = create_role(name="test_")
        self.crew_member = create_crew_member(role=self.role)

        self.url = photo_upload_url(self.crew_member.id)

    def tearDown(self) -> None:
        self.crew_member.photo.delete()

    def test_upload_photo_to_crew_member(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(self.url, {"photo": ntf}, format="multipart")
        self.crew_member.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("photo", response.data)
        self.assertTrue(os.path.exists(self.crew_member.photo.path))

    def test_upload_photo_bad_request(self) -> None:
        res = self.client.post(self.url, {"photo": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_photo_to_crew_member_list(self) -> None:
        url = CREW_MEMBER_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                url,
                {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "role": self.role.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        crew_member = CrewMember.objects.get(first_name="first_name")
        self.assertFalse(crew_member.photo)

    def test_photo_url_is_shown_on_crew_member_detail(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(self.url, {"photo": ntf}, format="multipart")
        response = self.client.get(detail_url(self.crew_member.id))

        self.assertIn("photo", response.data)
