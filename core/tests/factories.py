import random
import string
from django.contrib.auth import get_user_model

from core.models import (
    City,
    Airport,
    Route,
    Role,
    CrewMember,
    CrewGroup,
    AirplaneType,
    Airplane,
    SeatConfiguration,
    Flight,
    Order,
    Ticket
)
from user.models import User


def generate_random_iata_code():
    return "".join(random.choices(string.ascii_uppercase, k=3))


def create_city(as_dict: bool=False, **params) -> City | dict:
    defaults = {
        "name": "test_city",
        "country": "test_country"
    }
    defaults.update(params)
    return defaults if as_dict else City.objects.create(**defaults)


def create_airport(as_dict: bool=False, **params) -> Airport | dict:
    defaults = {
        "name": "test_airport",
        "iata_code": generate_random_iata_code(),
        "city": create_city()
    }
    defaults.update(params)
    if as_dict:
        defaults["city"] = defaults["city"].id
        return defaults
    return Airport.objects.create(**defaults)


def create_route(as_tuple: bool=False, **params) -> Route | tuple:
    defaults = {
        "source": create_airport(),
        "destination": create_airport(),
        "distance": 5555
    }
    defaults.update(params)
    if as_tuple:
        return Route.objects.create(**defaults), defaults
    return Route.objects.create(**defaults)


def create_role(as_dict: bool=False, **params) -> Role | dict:
    defaults = {
        "name": "test_role"
    }
    defaults.update(params)
    return defaults if as_dict else Role.objects.get_or_create(**defaults)[0]


def create_crew_member(as_dict: bool=False, **params) -> CrewMember | dict:
    defaults = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "role": create_role()
    }
    defaults.update(params)
    if as_dict:
        defaults["role"] = defaults["role"].id
        return defaults
    return CrewMember.objects.create(**defaults)


def create_crew_group(as_dict: bool=False, **params) -> CrewGroup | dict:
    defaults = {"crew_code": "BB222"}
    defaults.update(params)

    return defaults if as_dict else CrewGroup.objects.get_or_create(**defaults)[0]


def create_airplane_type(as_dict: bool=False, **params) -> AirplaneType | dict:
    defaults = {"name": "test_airplane_type"}
    defaults.update(params)
    airplane_type, created = AirplaneType.objects.get_or_create(**defaults)
    return defaults if as_dict else airplane_type


def create_airplane(as_dict: bool=False, **params) -> Airplane | dict:
    defaults = {
        "model_name": "test_model_name",
        "type": create_airplane_type()
    }
    defaults.update(params)
    return defaults if as_dict else Airplane.objects.create(**defaults)


def create_seat_configuration(as_dict: bool=False, **params) -> SeatConfiguration | dict:
    defaults = {
        "seats_class": "EC",
        "rows": 15,
        "seats_in_row": 5,
        "airplane": create_airplane()
    }
    defaults.update(params)
    return defaults if as_dict else SeatConfiguration.objects.create(**defaults)


def create_flight(as_dict: bool=False, **params) -> Flight | dict:
    defaults = {
        "flight_number": "AA1234",
        "route": create_route(),
        "airplane": create_airplane(),
        "departure_time": "2020-02-02 02:02:00",
        "arrival_time": "2020-02-02 22:02:00",
        "crew": create_crew_group()
    }
    defaults.update(params)
    return defaults if as_dict else Flight.objects.create(**defaults)


def create_order(as_tuple: bool=False, user: User=None, **params) -> Order | tuple:
    defaults = {
        "user": user or get_user_model().objects.create_user(email="test@user.com", password="test123user")
    }
    defaults.update(params)
    if as_tuple:
        return Order.objects.create(**defaults), defaults
    return Order.objects.create(**defaults)


def create_ticket(**params) -> Ticket:
    create_seat_configuration(
        seats_class=params.get("seat_class", "EC"),
        airplane=params.get("airplane", create_airplane(model_name="special"))
    )
    defaults = {
        "row": 1,
        "seat": 1,
        "passenger_first_name": "test_first_name",
        "passenger_last_name": "test_last_name",
        "seat_class": "EC",
        "flight": create_flight(
            airplane=params.pop("airplane", Airplane.objects.get(model_name="special"))
        ),
        "order": create_order()
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)
