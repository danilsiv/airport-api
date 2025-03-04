from django.test import TestCase
from django.core.exceptions import ValidationError

from core.models import City, Airport, Route, Role


def create_city(**params) -> City:
    defaults = {
        "name": "test_city",
        "country": "test_country"
    }
    defaults.update(params)

    return City.objects.create(**defaults)


def create_airport(**params) -> Airport:
    defaults = {
        "name": "test_airport",
        "iata_code": "TST",
        "city": create_city()
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def create_route(**params):
    defaults = {
        "source": create_airport(iata_code="AAA"),
        "destination": create_airport(iata_code="BBB"),
        "distance": 5555
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def create_role(name: str="test_role") -> Role:
    return Role.objects.create(name=name)


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
