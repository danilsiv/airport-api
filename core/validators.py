import re
from django.core.exceptions import ValidationError


def validate_iata_code_format(value: str) -> None:
    if not re.fullmatch(r"[A-Z]+", value):
        raise ValidationError("The IATA-code must contain only uppercase Latin letters.")

    if len(value) != 3:
        raise ValidationError("The IATA-code must consist of exactly 3 letters.")


def validate_flight_number_format(value: str) -> None:
    if not re.fullmatch(r"[A-Z0-9]{2}\d{1,4}", value):
        raise ValidationError("The flight number must start with 2 uppercase "
                              "Latin letters and end with 1 to 4 digits.")
