from django.test import TestCase
from django.core.exceptions import ValidationError

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
)


class CityTest(TestCase):
    def test_str_method(self) -> None:
        city = create_city()
        self.assertEqual(str(city), city.name)


class AirportTest(TestCase):
    def test_iata_code_validation(self) -> None:
        airport = create_airport(iata_code="invalid")
        with self.assertRaises(ValidationError):
            airport.full_clean()

    def test_str_method(self) -> None:
        airport = create_airport()
        self.assertEqual(str(airport), f"{airport.name} {airport.iata_code}")


class RouteTest(TestCase):
    def test_route_code_attribute(self) -> None:
        route = create_route()
        self.assertTrue(route.route_code)
        expected_result = f"{route.source.iata_code}-{route.destination.iata_code}"
        self.assertEqual(route.route_code, expected_result)

    def test_name_property(self) -> None:
        route = create_route()
        expected_result = f"{route.source.city.name} - {route.destination.city.name}"
        self.assertTrue(route.name)
        self.assertEqual(route.name, expected_result)

    def test_unique_source_and_destination_validation(self) -> None:
        airport = create_airport()
        with self.assertRaises(ValidationError):
            create_route(source=airport, destination=airport)

    def test_str_method(self) -> None:
        route = create_route()
        self.assertEqual(str(route), route.route_code)


class RoleTest(TestCase):
    def test_str_method(self) -> None:
        role = create_role()
        self.assertEqual(str(role), role.name)


class CrewMemberTest(TestCase):
    def test_full_name_property(self) -> None:
        member = create_crew_member()
        self.assertTrue(member.full_name)
        self.assertEqual(member.full_name, f"{member.first_name} {member.last_name}")

    def test_str_method(self) -> None:
        member = create_crew_member()
        expected_result = f"{member.first_name} {member.last_name} ({member.role.name})"
        self.assertEqual(str(member), expected_result)


class CrewGroupTest(TestCase):
    def test_description_property(self) -> None:
        crew_group = create_crew_group()
        self.assertTrue(crew_group.description)
        self.assertEqual(crew_group.description, "Unassigned crew")

    def test_str_method(self) -> None:
        crew_group = create_crew_group()
        self.assertEqual(str(crew_group), f"Crew {crew_group.crew_code}")


class AirplaneTypeTest(TestCase):
    def test_str_method(self) -> None:
        airplane_type = create_airplane_type()
        self.assertEqual(str(airplane_type), airplane_type.name)


class AirplaneTest(TestCase):
    def test_str_method(self) -> None:
        airplane = create_airplane()
        self.assertEqual(str(airplane), airplane.model_name)


class SeatConfigurationTest(TestCase):
    def test_num_of_seats_property(self) -> None:
        conf = create_seat_configuration()
        self.assertTrue(conf.num_of_seats)
        self.assertEqual(conf.num_of_seats, conf.seats_in_row * conf.rows)

    def test_str_method(self) -> None:
        conf = create_seat_configuration()
        expected_result = (f"{conf.get_seats_class_display()} "
                           f"Configuration ({conf.airplane.model_name})")
        self.assertEqual(str(conf), expected_result)
