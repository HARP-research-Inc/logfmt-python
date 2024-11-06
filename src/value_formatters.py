from typing import Mapping, Any, Iterable
import types
import dataclasses


def format_mapping(value: Mapping) -> tuple[dict[str, Any], bool]:
    return {str(key): value for key, value in value.items()}, True


def format_iterable(value: Iterable) -> tuple[dict[str, Any], bool]:
    return {str(i): item for i, item in enumerate(value)}, True


def format_namespace(value: types.SimpleNamespace) -> tuple[dict[str, Any], bool]:
    return {str(key): value for key, value in value.__dict__.items()}, False


def format_dataclass(value) -> tuple[dict[str, Any], bool]:
    mapped_format = format_mapping(value.model_dump().items())[0]
    return mapped_format, False

def format_namedtuple(value: tuple) -> tuple[dict[str, Any], bool]:
    return value._asdict(), False


default_formatters = {
    Mapping: format_mapping,
    Iterable: format_iterable,
    types.SimpleNamespace: format_namespace,
    (lambda value: dataclasses.is_dataclass(value) and not isinstance(value, type)): format_dataclass,
    (lambda value: isinstance(value, tuple) and hasattr(value, "_asdict")): format_namedtuple,
}
