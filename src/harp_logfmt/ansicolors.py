from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class _REGULAR:
    BLACK: Literal["\x1b[0;30m"] = "\x1b[0;30m"
    RED: Literal["\x1b[0;31m"] = "\x1b[0;31m"
    GREEN: Literal["\x1b[0;32m"] = "\x1b[0;32m"
    YELLOW: Literal["\x1b[0;33m"] = "\x1b[0;33m"
    BLUE: Literal["\x1b[0;34m"] = "\x1b[0;34m"
    PURPLE: Literal["\x1b[0;35m"] = "\x1b[0;35m"
    CYAN: Literal["\x1b[0;36m"] = "\x1b[0;36m"
    WHITE: Literal["\x1b[0;37m"] = "\x1b[0;37m"


@dataclass(frozen=True)
class _BOLD:
    BLACK: Literal["\x1b[1;30m"] = "\x1b[1;30m"
    RED: Literal["\x1b[1;31m"] = "\x1b[1;31m"
    GREEN: Literal["\x1b[1;32m"] = "\x1b[1;32m"
    YELLOW: Literal["\x1b[1;33m"] = "\x1b[1;33m"
    BLUE: Literal["\x1b[1;34m"] = "\x1b[1;34m"
    PURPLE: Literal["\x1b[1;35m"] = "\x1b[1;35m"
    CYAN: Literal["\x1b[1;36m"] = "\x1b[1;36m"
    WHITE: Literal["\x1b[1;37m"] = "\x1b[1;37m"


@dataclass(frozen=True)
class _ANSIColors:
    # https://gist.github.com/JBlond/2fea43a3049b38287e5e9cefc87b2124
    # \e -> \x1b
    RESET: Literal["\x1b[0m"] = "\x1b[0m"
    REGULAR: _REGULAR = _REGULAR()
    BOLD: _BOLD = _BOLD()


ANSIColors = _ANSIColors()
