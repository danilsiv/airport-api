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


def create_crew_member(**params) -> CrewMember:
    defaults = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "role": create_role()
    }
    defaults.update(params)
    return CrewMember.objects.create(**defaults)


def create_crew_group(crew_code: str="BB222", **params) -> CrewGroup:
    crew_group = CrewGroup.objects.create(crew_code=crew_code)

    crew_group.pilots.set(params.get("pilots", []))
    crew_group.pilots.set(params.get("stewards", []))
    crew_group.pilots.set(params.get("technicians", []))
    crew_group.pilots.set(params.get("additional_staff", []))

    return crew_group


def create_airplane_type(name: str="test_airplane_type") -> AirplaneType:
    airplane_type, created = AirplaneType.objects.get_or_create(name=name)
    return airplane_type


def create_airplane(**params) -> Airplane:
    defaults = {
        "model_name": "test_model_name",
        "type": create_airplane_type()
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def create_seat_configuration(**params) -> SeatConfiguration:
    defaults = {
        "seats_class": "EC",
        "rows": 15,
        "seats_in_row": 5,
        "airplane": create_airplane()
    }
    defaults.update(params)
    return SeatConfiguration.objects.create(**defaults)


def create_flight(**params) -> Flight:
    defaults = {
        "flight_number": "AA1234",
        "route": create_route(),
        "airplane": create_airplane(),
        "departure_time": "2020-02-02 02:02:00",
        "arrival_time": "2020-02-02 22:02:00",
        "crew": create_crew_group()
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


def create_order(**params) -> Order:
    defaults = {
        "user": User.objects.create_user(email="test@user.com", password="test1234user")
    }
    defaults.update(params)
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
