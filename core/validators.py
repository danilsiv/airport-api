import re
from django.core.exceptions import ValidationError


def validate_iata_code_format(value: str) -> None:
    if not re.fullmatch(r"[A-Z]+", value):
        raise ValidationError("The IATA-code must contain only uppercase Latin letters.")

    if len(value) != 3:
        raise ValidationError("The IATA-code must consist of exactly 3 letters.")
