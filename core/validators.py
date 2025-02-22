import re
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

import core.models


def validate_iata_code_format(value: str) -> None:
    if not re.fullmatch(r"[A-Z]+", value):
        raise DjangoValidationError("The IATA-code must contain only uppercase Latin letters.")

    if len(value) != 3:
        raise DjangoValidationError("The IATA-code must consist of exactly 3 letters.")


def validate_flight_number_format(value: str) -> None:
    if not re.fullmatch(r"[A-Z0-9]{2}\d{1,4}", value):
        raise DjangoValidationError("The flight number must start with 2 uppercase "
                              "Latin letters and end with 1 to 4 digits.")


def validate_seat_class(value: str) -> None:
    seats_classes = [conf[0] for conf in core.models.SEATS_CLASS_CHOICES]
    if value not in seats_classes:
        valid_choices = ", ".join(seats_classes)
        raise DRFValidationError(f"Invalid seat class. Choose from: {valid_choices}.")
