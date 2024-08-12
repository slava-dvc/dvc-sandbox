import logging
from typing import Dict, Callable
from urllib.parse import urlparse

__all__ = ['field_serializers']


def _boolean_serializer(value):
    value = str(value)  # Handle None values as well
    if value.lower() not in {'1', 'true', 'yes', '0', 'false', 'no'}:
        raise ValueError(f"{value} can't be cast to boolean")
    return value.lower() in {'1', 'true', 'yes'}


def _get_value(value: list | tuple | str | int | float):
    if isinstance(value, (list, tuple)):
        if len(value) > 1:
            logging.error(f"Invalid value for field, got {value}")
            return None
        value = value[0]

    if not isinstance(value, (str, int, float)):
        raise ValueError(f"Invalid value for filed, got {value}")
    return value


def _text_serializer(value):
    value = _get_value(value)
    if not value:
        return None
    return str(value)


def _url_serializer(value):
    value = _get_value(value)
    if not value:
        return None

    try:
        result = urlparse(str(value))
        if all([result.scheme, result.netloc]):
            return str(value)
        else:
            logging.warning(f"Invalid URL: {value}")
            return None
    except Exception:
        logging.warning(f"Invalid URL: {value}")
        return None


def _number_serializer(value):
    value = _get_value(value)
    if not value:
        return None

    if isinstance(value, (int, float)):
        return value

    # type(value) is always a string here
    if value.lower() == 'unknown':
        return None

    # Handle numbers like $20M, 20k, $60.71 million
    multiples = {'k': 1000, 'm': 1000000}
    value = value.lower().replace(',', '').replace('$', '').replace(' million', 'm')
    if not value:
        return None
    multiplier = 1

    try:
        if value[-1] in multiples:
            multiplier *= multiples[value[-1]]
            value = value[:-1]
    except KeyError as e:
        raise ValueError(f"{value} is not a number can be converted")

    try:
        if '.' in value:
            return float(value) * multiplier

        return int(value) * multiplier
    except ValueError:
        logging.warning(f"{value} is not a number can be converted")
        return None


def _multiple_selects_serializer(value):
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]


field_serializers: Dict[str, Callable] = {
    'checkbox': _boolean_serializer,
    'currency': _number_serializer,
    'date': _text_serializer,
    'email': _text_serializer,
    'multilineText': _text_serializer,
    'multipleLookupValues': _multiple_selects_serializer,
    'multipleRecordLinks': _multiple_selects_serializer,
    'multipleSelects': _multiple_selects_serializer,
    'number': _number_serializer,
    'richText': _text_serializer,
    'singleLineText': _text_serializer,
    'singleSelect': _text_serializer,
    'url': _url_serializer,
}

readonly_fields = {
    'aiText',
    'button',
    'count',
    'count',
    'createdBy',
    'createdTime',
    'formula',
    'lastModifiedBy',
    'lastModifiedTime',
    'multipleAttachments',
    'multipleCollaborators',
    'rollup',
}
