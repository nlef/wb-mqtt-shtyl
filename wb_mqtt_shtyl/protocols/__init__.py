from .base import UpsParser
from .megatec import MegatecParser
from .shtyl import ShtylParser

PARSERS = {
    "shtyl": ShtylParser,
    "megatec": MegatecParser,
}

SERIAL_SETTINGS = {
    "shtyl": {"baudrate": 14400, "timeout": 0.7},
    "megatec": {"baudrate": 2400, "xonxoff": True, "timeout": 1},
}

__all__ = ["PARSERS", "SERIAL_SETTINGS", "MegatecParser", "ShtylParser", "UpsParser"]
