import logging
import re
import sys
from typing import Any, Callable, Container, Iterable
import datetime
from .ansicolors import ANSIColors
from .value_formatters import default_formatters

CUSTOM_FORMATTER_PREDICATE_FUNC = Callable[[Any], bool]
CUSTOM_FORMATTER_PREDICATE = type | CUSTOM_FORMATTER_PREDICATE_FUNC
CUSTOM_FORMATTER_FUNC_RETURN = tuple[dict[str, Any], bool]
CUSTOM_FORMATTER_FUNC = Callable[
    [Any], CUSTOM_FORMATTER_FUNC_RETURN
]  # Returns a dict of {key: value} pairs and a boolean indicating whether to use getitem syntax (getitem syntax = '[key]=value', non-getitem syntax = '.key=value')


class LogfmtFormatter(logging.Formatter):
    """A logfmt formatter for Python's logging module."""

    def __init__(
        self,
        *args,
        colorize: bool = True,
        exclude_keys: Iterable[str] = (),
        msg_regex: str | re.Pattern | None = None,
        highlight_keys: Iterable[str] = ("message",),
        include_default_formatters: bool = True,
        timezone: datetime.tzinfo = datetime.timezone.utc,
        **kwargs,
    ):
        kwargs.setdefault("datefmt", "%Y-%m-%dT%H:%M:%S%.%f%z")
        super().__init__(*args, **kwargs)
        self._exclude_keys = set(exclude_keys)
        self.colorize = colorize
        self._msg_regex: re.Pattern | None = re.compile(msg_regex) if isinstance(msg_regex, str) else msg_regex
        self._highlight_keys = set(highlight_keys)
        self.custom_formatters: dict[CUSTOM_FORMATTER_PREDICATE, CUSTOM_FORMATTER_FUNC] = {}
        self.timezone = timezone
        if include_default_formatters:
            self.custom_formatters.update(default_formatters)

    @property
    def exclude_keys(self) -> Container[str]:
        return self._exclude_keys

    @exclude_keys.setter
    def exclude_keys(self, value: Iterable[str]):
        self._exclude_keys = set(value)

    @property
    def msg_regex(self) -> re.Pattern | None:
        return self._msg_regex

    @msg_regex.setter
    def msg_regex(self, value: str | re.Pattern | None):
        self._msg_regex = re.compile(value) if isinstance(value, str) else value

    @property
    def highlight_keys(self) -> Container[str]:
        return self._highlight_keys

    @highlight_keys.setter
    def highlight_keys(self, value: Iterable[str]):
        self._highlight_keys = set(value)

    @msg_regex.setter
    def msg_regex(self, value: str | re.Pattern | None):
        self._msg_regex = re.compile(value) if isinstance(value, str) else value

    def kv_to_logfmt(self, key: str, value: str) -> str:
        realkey = f"{ANSIColors.BOLD.BLACK}{key}={ANSIColors.RESET}" if self.colorize else (key + "=")
        realvalue = (
            f"{ANSIColors.REGULAR.BLACK}{value}{ANSIColors.RESET}"
            if self.colorize and key not in self._highlight_keys
            else str(value)
        )
        quotechar = f'{ANSIColors.REGULAR.BLACK}"{ANSIColors.RESET}' if self.colorize else '"'
        if " " in realvalue:
            return f"{realkey}{quotechar}{realvalue}{quotechar}"
        return f"{realkey}{realvalue}"

    level_words_colored = {
        logging.DEBUG: f"{ANSIColors.REGULAR.BLACK}DEBUG{ANSIColors.RESET}",
        logging.INFO: f"{ANSIColors.REGULAR.CYAN}INFO{ANSIColors.RESET}",
        logging.WARNING: f"{ANSIColors.REGULAR.YELLOW}WARNING{ANSIColors.RESET}",
        logging.ERROR: f"{ANSIColors.REGULAR.RED}ERROR{ANSIColors.RESET}",
        logging.CRITICAL: f"{ANSIColors.BOLD.RED}CRITICAL{ANSIColors.RESET}",
    }

    level_words = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    default_logrecord_attributes = [
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
        "data",  # Technically this is not part of the default log record but we specially handle this attribute
    ]

    def colorize_level_if_debug(self, levelno: int) -> str:
        if self.colorize:
            return LogfmtFormatter.level_words_colored[levelno]
        return LogfmtFormatter.level_words[levelno]

    def _format_value(self, value: Any, prefix: str) -> dict[str, str]:
        if isinstance(value, str):
            return {prefix: value}
        for formatter_type, formatter in reversed(self.custom_formatters.items()):
            if isinstance(formatter_type, type):
                is_formatter_type = isinstance(value, formatter_type)
            else:
                is_formatter_type = formatter_type(value)
            if is_formatter_type:
                base: dict[str, str] = {}
                # new_keys is a dict of {"key": "value"} pairs
                # If as_getitem, the final keys will be {f"{prefix}[{key}]": value}
                # If not as_getitem, the final keys will be {f"{prefix}.{key}": value}
                new_data, as_getitem = formatter(value)
                for key, value in new_data.items():
                    expanded = self._format_value(value, f"{prefix}[{key}]" if as_getitem else f"{prefix}.{key}")
                    base.update(expanded)
                return base
        return {prefix: str(value)}

    def format(self, record: logging.LogRecord) -> str:
        dt = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc).astimezone(self.timezone)
        data = {
            "time": dt.isoformat("T"),
            "function": record.funcName,
        }
        if sys.version_info >= (3, 12):
            data["taskName"] = record.taskName
        data.update(
            {
                key: (value if isinstance(value, str) and value is not None else str(value))
                for key, value in record.__dict__.items()
                if key not in self.default_logrecord_attributes
            }
        )
        data.update(
            {"name": record.name, "level": self.colorize_level_if_debug(record.levelno)}
        )  # We put this last because we always want this to be last
        if not isinstance(record.msg, str):
            msg = record.msg
            data.update(self._format_value(msg, "message"))
        elif self.msg_regex:
            match = self.msg_regex.search(record.getMessage())
            if match:
                groups = match.groupdict()
                if not groups:
                    raise ValueError("msg_regex must have at least one named group.")
                del data["message"]
                data.update(groups)
        else:
            data["message"] = record.getMessage()
        if (attr := getattr(record, "data", None)) is not None:
            data.update(self._format_value(attr, "data"))
        if self._exclude_keys:
            common_keys = set(data.keys()) & self._exclude_keys
            for key in common_keys:
                del data[key]
        for key, value in data.copy().items():
            if value is None:
                del data[key]
        base = " ".join([self.kv_to_logfmt(key, value) for key, value in data.items()])
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        if record.stack_info:
            base += "\n" + self.formatStack(record.stack_info)
        return base

    def add_custom_formatter(self, condition: CUSTOM_FORMATTER_PREDICATE, formatter: CUSTOM_FORMATTER_FUNC):
        self.custom_formatters[condition] = formatter

    def custom_formatter(self, condition: CUSTOM_FORMATTER_PREDICATE):
        """Decorator form of add_custom_formatter"""

        def decorator(func: CUSTOM_FORMATTER_FUNC) -> CUSTOM_FORMATTER_FUNC:
            self.add_custom_formatter(condition, func)
            return func

        return decorator

    def remove_custom_formatter(self, condition: CUSTOM_FORMATTER_PREDICATE):
        del self.custom_formatters[condition]
