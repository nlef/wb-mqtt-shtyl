from .base import UpsParser
from .shtyl import ShtylParser
from .megatec import MegatecParser

PARSERS = {
    "shtyl": ShtylParser,
    "megatec": MegatecParser,
}

SERIAL_SETTINGS = {
    "shtyl": {"baudrate": 14400, "timeout": 0.7},
    "megatec": {"baudrate": 2400, "xonxoff": True, "timeout": 1},
}

__all__ = ["UpsParser", "ShtylParser", "MegatecParser", "PARSERS", "SERIAL_SETTINGS"]
