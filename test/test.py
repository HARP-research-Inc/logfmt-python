from harp_logfmt import LogfmtFormatter, CUSTOM_FORMATTER_FUNC_RETURN
from unittest import TestCase
from dataclasses import dataclass
from typing import NamedTuple
from harp_logfmt.ansicolors import ANSIColors
from uuid import uuid4
import logging
import io


@dataclass(frozen=True)
class SimpleDataclass:
    a: int
    b: int
    c: int


class SimpleNamedTuple(NamedTuple):
    a: int
    b: int
    c: int


def setup_logger(formatter: logging.Formatter, *, name: str | None = None) -> tuple[logging.Logger, io.StringIO]:
    """Returns a function that, when given a Formatter, will return a unique Logger and the StringIO to which it prints."""
    logger = logging.getLogger(name or str(uuid4()))
    logger.setLevel(logging.DEBUG)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, stream


class TestSimple(TestCase):
    def test_simple(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="simple")
        logger.debug("Hello, world!")
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn('message="Hello, world!"', value)
        self.assertIn("function=test_simple", value)
        self.assertIn("name=simple", value)

    def test_simple_list(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="simple_list")
        logger.debug([1, 2, 3])
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[0]=1", value)
        self.assertIn("message[1]=2", value)
        self.assertIn("message[2]=3", value)
        self.assertIn("function=test_simple_list", value)
        self.assertIn("name=simple_list", value)

    def test_simple_dict(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="simple_dict")
        logger.debug({"a": 1, "b": 2, "c": 3})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[a]=1", value)
        self.assertIn("message[b]=2", value)
        self.assertIn("message[c]=3", value)
        self.assertIn("function=test_simple_dict", value)
        self.assertIn("name=simple_dict", value)

    def test_simple_dataclass(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="simple_dataclass")
        logger.debug(SimpleDataclass(1, 2, 3))
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message.a=1", value)
        self.assertIn("message.b=2", value)
        self.assertIn("message.c=3", value)
        self.assertIn("function=test_simple_dataclass", value)
        self.assertIn("name=simple_dataclass", value)

    def test_simple_namedtuple(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="simple_namedtuple")
        logger.debug(SimpleNamedTuple(1, 2, 3))
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message.a=1", value)
        self.assertIn("message.b=2", value)
        self.assertIn("message.c=3", value)
        self.assertIn("function=test_simple_namedtuple", value)
        self.assertIn("name=simple_namedtuple", value)

    def test_simple_colorized(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=True), name="simple_colorized")
        logger.debug("Hello, world!")
        value = stream.getvalue()
        self.assertIn(
            f"{ANSIColors.BOLD.BLACK}function={ANSIColors.RESET}{ANSIColors.REGULAR.BLACK}test_simple_colorized{ANSIColors.RESET}",
            value,
        )
        self.assertIn(
            f"{ANSIColors.BOLD.BLACK}level={ANSIColors.RESET}{ANSIColors.REGULAR.BLACK}{ANSIColors.REGULAR.BLACK}DEBUG{ANSIColors.RESET}",
            value,
        )
        self.assertIn(
            f"{ANSIColors.BOLD.BLACK}name={ANSIColors.RESET}{ANSIColors.REGULAR.BLACK}simple_colorized{ANSIColors.RESET}",
            value,
        )
        self.assertIn(
            f'{ANSIColors.BOLD.BLACK}message={ANSIColors.RESET}{ANSIColors.REGULAR.BLACK}"{ANSIColors.RESET}Hello, world!{ANSIColors.REGULAR.BLACK}"{ANSIColors.RESET}',
            value,
        )

    def test_nested_two_layers(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="nested_two_layers")
        logger.debug({"a": {"b": 1}})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[a][b]=1", value)
        self.assertIn("function=test_nested_two_layers", value)
        self.assertIn("name=nested_two_layers", value)

    def test_nested_mixed_two_layers(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="nested_mixed_two_layers")
        logger.debug({"a": [1, 2, 3]})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[a][0]=1", value)
        self.assertIn("message[a][1]=2", value)
        self.assertIn("message[a][2]=3", value)
        self.assertIn("function=test_nested_mixed_two_layers", value)
        self.assertIn("name=nested_mixed_two_layers", value)

    def test_nested_mixed_dataclass_list_two_layers(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="nested_mixed_dataclass_list_two_layers")
        logger.debug([SimpleDataclass(1, 2, 3), SimpleDataclass(4, 5, 6)])
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[0].a=1", value)
        self.assertIn("message[0].b=2", value)
        self.assertIn("message[0].c=3", value)
        self.assertIn("message[1].a=4", value)
        self.assertIn("message[1].b=5", value)
        self.assertIn("message[1].c=6", value)
        self.assertIn("function=test_nested_mixed_dataclass_list_two_layers", value)
        self.assertIn("name=nested_mixed_dataclass_list_two_layers", value)

    def test_nested_three_layers(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="nested_three_layers")
        logger.debug({"a": {"b": {"c": 1}}})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[a][b][c]=1", value)
        self.assertIn("function=test_nested_three_layers", value)
        self.assertIn("name=nested_three_layers", value)

    def test_nested_mixed_three_layers(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="nested_mixed_three_layers")
        logger.debug({"a": [1, {"b": 2}]})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[a][0]=1", value)
        self.assertIn("message[a][1][b]=2", value)
        self.assertIn("function=test_nested_mixed_three_layers", value)
        self.assertIn("name=nested_mixed_three_layers", value)

    def test_all_default_types(self):
        logger, stream = setup_logger(LogfmtFormatter(colorize=False), name="all_default_types")
        logger.debug(
            {
                "a": 1,
                "b": [2, 3],
                "c": {"d": 4},
                "e": SimpleDataclass(5, 6, 7),
                "f": SimpleNamedTuple(8, 9, 10),
            }
        )
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[a]=1", value)
        self.assertIn("message[b][0]=2", value)
        self.assertIn("message[b][1]=3", value)
        self.assertIn("message[c][d]=4", value)
        self.assertIn("message[e].a=5", value)
        self.assertIn("message[e].b=6", value)
        self.assertIn("message[e].c=7", value)
        self.assertIn("message[f].a=8", value)
        self.assertIn("message[f].b=9", value)
        self.assertIn("message[f].c=10", value)
        self.assertIn("function=test_all_default_types", value)
        self.assertIn("name=all_default_types", value)

    def test_custom_formatter(self):
        formatter = LogfmtFormatter(colorize=False)
        logger, stream = setup_logger(formatter, name="custom_formatter")

        @formatter.custom_formatter(lambda value: type(value) is complex)
        def complex_formatter(value: complex) -> CUSTOM_FORMATTER_FUNC_RETURN:
            return {"real": value.real, "imag": value.imag}, True

        @formatter.custom_formatter(float)
        def float_formatter(value: float) -> CUSTOM_FORMATTER_FUNC_RETURN:
            return {"integer": int(value), "fraction": str(value % 1)}, False

        logger.debug([42, 42.5, complex(42, 0.5)])
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[0]=42", value)
        self.assertIn("message[1].integer=42", value)
        self.assertIn("message[1].fraction=0.5", value)
        self.assertIn("message[2][real].integer=42", value)
        self.assertIn("message[2][real].fraction=0.0", value)
        self.assertIn("message[2][imag].integer=0", value)
        self.assertIn("message[2][imag].fraction=0.5", value)
        self.assertIn("function=test_custom_formatter", value)
        self.assertIn("name=custom_formatter", value)

    def test_msg_and_data_simple(self):
        formatter = LogfmtFormatter(colorize=False)
        logger, stream = setup_logger(formatter, name="msg_and_data_simple")
        logger.debug("Hello, world!", extra={"data": "World, Hello!"})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn('message="Hello, world!"', value)
        self.assertIn('data="World, Hello!"', value)
        self.assertIn("function=test_msg_and_data_simple", value)
        self.assertIn("name=msg_and_data_simple", value)

    def test_msg_and_data_complex(self):
        formatter = LogfmtFormatter(colorize=False)
        logger, stream = setup_logger(formatter, name="msg_and_data_complex")
        logger.debug("Hello, world!", extra={"data": {"a": 1, "b": 2}})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn('message="Hello, world!"', value)
        self.assertIn("data[a]=1", value)
        self.assertIn("data[b]=2", value)
        self.assertIn("function=test_msg_and_data_complex", value)
        self.assertIn("name=msg_and_data_complex", value)

    def test_both_msg_and_data_non_string(self):
        formatter = LogfmtFormatter(colorize=False)
        logger, stream = setup_logger(formatter, name="both_msg_and_data_non_string")
        logger.debug([42], extra={"data": [42]})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[0]=42", value)
        self.assertIn("data[0]=42", value)
        self.assertIn("function=test_both_msg_and_data_non_string", value)
        self.assertIn("name=both_msg_and_data_non_string", value)

    def test_both_msg_and_data_custom_formatter(self):
        formatter = LogfmtFormatter(colorize=False)
        logger, stream = setup_logger(formatter, name="both_msg_and_data_custom_formatter")

        @formatter.custom_formatter(lambda value: type(value) is complex)
        def complex_formatter(value: complex) -> CUSTOM_FORMATTER_FUNC_RETURN:
            return {"real": value.real, "imag": value.imag}, True

        logger.debug(complex(21, 1), extra={"data": complex(21, 1)})
        value = stream.getvalue()
        self.assertIn("level=DEBUG", value)
        self.assertIn("message[real]=21", value)
        self.assertIn("message[imag]=1", value)
        self.assertIn("data[real]=21", value)
        self.assertIn("data[imag]=1", value)
        self.assertIn("function=test_both_msg_and_data_custom_formatter", value)
        self.assertIn("name=both_msg_and_data_custom_formatter", value)
