from multiprocessing.dummy import Namespace as MultiprocessingDummyNamespace
from multiprocessing.managers import Namespace as MulltiprocessingManagersNamespace
from typing import Any
from collections.abc import Mapping, Iterable
import types
import dataclasses
import argparse


def format_mapping(value: Mapping) -> tuple[dict[str, Any], bool]:
    return {str(key): value for key, value in value.items()}, True


def format_iterable(value: Iterable) -> tuple[dict[str, Any], bool]:
    return {str(i): item for i, item in enumerate(value)}, True


def format_namespace(
    value: types.SimpleNamespace
    | argparse.Namespace
    | MultiprocessingDummyNamespace
    | MulltiprocessingManagersNamespace,
) -> tuple[dict[str, Any], bool]:
    return {str(key): value for key, value in value.__dict__.items()}, False


def format_dataclass(value) -> tuple[dict[str, Any], bool]:
    return {field.name: getattr(value, field.name) for field in dataclasses.fields(value)}, False


def format_namedtuple(value: tuple) -> tuple[dict[str, Any], bool]:
    return value._asdict(), False


default_formatters = {
    Iterable: format_iterable,  # Goes to top because it is the most generic
    Mapping: format_mapping,
    (
        types.SimpleNamespace,
        argparse.Namespace,
        MultiprocessingDummyNamespace,
        MulltiprocessingManagersNamespace,
    ): format_namespace,
    (lambda value: dataclasses.is_dataclass(value) and not isinstance(value, type)): format_dataclass,
    (lambda value: isinstance(value, tuple) and hasattr(value, "_asdict")): format_namedtuple,
}
