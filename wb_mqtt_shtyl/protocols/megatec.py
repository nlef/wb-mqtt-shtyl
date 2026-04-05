import logging

import serial
from serial import Serial

from .base import UpsParser

LOGGER = logging.getLogger(__name__)


class MegatecParser(UpsParser):
    device_id = "shtyl_ups"
    state_keys = [
        "input_voltage",
        "output_voltage",
        "output_load",
        "input_frequency",
        "battery_voltage",
        "temperature",
    ]
    controls = [
        (
            "input_voltage",
            {
                "order": 0,
                "title": {"en": "Input voltage", "ru": "Входное напряжение"},
                "type": "voltage",
            },
        ),
        (
            "output_voltage",
            {
                "order": 1,
                "title": {"en": "Output voltage", "ru": "Выходное напряжение"},
                "type": "voltage",
            },
        ),
        (
            "output_load",
            {
                "order": 2,
                "title": {"en": "Output load", "ru": "Выходная нагрузка"},
                "type": "value",
                "units": "%",
            },
        ),
        (
            "input_frequency",
            {
                "order": 3,
                "title": {"en": "Input frequency", "ru": "Входная частота"},
                "type": "value",
                "units": "Hz",
            },
        ),
        (
            "battery_voltage",
            {
                "order": 4,
                "title": {"en": "Battery voltage", "ru": "Напряжение батареи"},
                "type": "voltage",
            },
        ),
        (
            "temperature",
            {
                "order": 5,
                "title": {"en": "Temperature", "ru": "Температура"},
                "type": "temperature",
            },
        ),
    ]

    def get_command(self) -> bytes:
        return b"Q1\r"

    def test_connection(self, serial_port: Serial) -> bool:
        LOGGER.debug("Testing Megatec connection...")
        serial_port.write(b"Q1\r")
        try:
            res = serial_port.read(1)
            return res != b""
        except serial.SerialException:
            LOGGER.exception("Serial exception")
            return False

    def parse(self, data: bytes) -> dict:
        vals = data.decode("utf-8").strip().strip("(").split(" ")
        return {
            "input_voltage": float(vals[0]),
            "output_voltage": float(vals[2]),
            "output_load": int(vals[3]),
            "input_frequency": float(vals[4]),
            "battery_voltage": float(vals[5]),
            "temperature": float(vals[6]),
        }
