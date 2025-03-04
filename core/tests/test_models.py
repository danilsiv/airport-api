from django.test import TestCase
from django.core.exceptions import ValidationError

from core.models import City, Airport


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
