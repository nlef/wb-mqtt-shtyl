import argparse
import json
import logging
import os
import queue
import sys
import threading
import time

from serial import Serial

from wb_common.mqtt_client import MQTTClient
from .protocols import PARSERS, SERIAL_SETTINGS

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_CONFIG_ERROR = 6

CONFIG_FILEPATH = os.environ.get("CONFIG_FILEPATH", "/etc/wb-mqtt-shtyl.conf")
SCHEMA_FILEPATH = os.environ.get(
    "SCHEMA_FILEPATH", "/usr/share/wb-mqtt-confed/schemas/wb-mqtt-shtyl.schema.json"
)

LOGGER = logging.getLogger(__name__)


class UPSService:
    def __init__(
        self,
        ups_type: str,
        serial_port: str = "/dev/ttyUSB0",
        broker_url: str = "tcp://localhost:1883",
    ):
        self._term_event = threading.Event()
        self._queue = queue.Queue()
        self._parser = PARSERS[ups_type]()

        self._logger = logging.getLogger(f"{__name__}.UPSService")

        self._client = MQTTClient(
            client_id_prefix="wb-mqtt-shtyl", broker_url=broker_url
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._mqtt_was_disconnected = False

        serial_kwargs = SERIAL_SETTINGS[ups_type].copy()
        serial_kwargs.update(
            {
                "port": serial_port,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
            }
        )
        self._serial = Serial(**serial_kwargs)
        self._serial_connected = False

    def _publish_control(self, device_id: str, control_id: str, meta=None, value=None):
        base_path = f"/devices/{device_id}/controls/{control_id}"
        if meta:
            self._client.publish(
                f"{base_path}/meta",
                json.dumps(meta, ensure_ascii=False),
                qos=1,
                retain=True,
            )
        if value is not None:
            self._client.publish(base_path, value, qos=1, retain=True)

    def _on_connect(self, _client, _userdata, _flags, rc):
        if rc != 0:
            self._logger.error(f"MQTT client connected with rc {rc}")
            return
        self._logger.info("MQTT client connected")
        if self._mqtt_was_disconnected:
            self._logger.info("Republish controls")

    def _on_disconnect(self, _client, _userdata, _flags):
        self._mqtt_was_disconnected = True
        self._logger.info("MQTT client disconnected")

    def _on_message(self, _client, _userdata, msg):
        self._queue.put(msg.payload.decode("utf-8"))

    def _publish_device(self):
        device_id = self._parser.device_id
        self._client.publish(
            f"/devices/{device_id}/meta",
            json.dumps(
                {
                    "driver": "wb-mqtt-shtyl",
                    "title": {"en": "Shtyl UPS", "ru": "ИБП Штиль"},
                },
                ensure_ascii=False,
            ),
            qos=1,
            retain=True,
        )
        for control_id, meta in self._parser.controls:
            self._publish_control(device_id, control_id, meta)

    def _publish_state(self, state: dict):
        device_id = self._parser.device_id
        for key in self._parser.state_keys:
            self._publish_control(device_id, key, value=state[key])
        if "alerts" in state and "alerts" in self._parser.state_keys:
            if state["alerts"]:
                self._client.publish(
                    f"/devices/{device_id}/controls/alerts/meta/error",
                    "r",
                    qos=1,
                    retain=True,
                )
            else:
                self._client.publish(
                    f"/devices/{device_id}/controls/alerts/meta/error",
                    None,
                    qos=1,
                    retain=True,
                )

    def _do_work(self):
        from .protocols import MegatecParser

        self._publish_device()
        while not self._term_event.is_set():
            while not self._serial_connected:
                try:
                    self._serial.flush()
                    self._serial_connected = self._parser.test_connection(self._serial)
                except Exception as e:
                    self._logger.warning(f"Serial connection error: {e}")
                if not self._serial_connected and isinstance(
                    self._parser, MegatecParser
                ):
                    self._serial.close()
                    self._serial.open()

            self._serial.flush()
            self._serial.write(self._parser.get_command())
            answ = self._serial.read_until(b"\r")

            try:
                res = self._parser.parse(answ)
                self._publish_device()
                self._publish_state(res)
            except Exception as e:
                self._logger.error(f"Parse error: {e}")

            self._logger.debug(f"Raw response: {answ!r}")
            time.sleep(1)

    def run(self):
        try:
            self._logger.info("Starting MQTT client")
            self._client.start()
            self._do_work()
        except ConnectionError:
            self._logger.error("MQTT connection error!")
            return EXIT_FAILURE
        except RuntimeError:
            self._logger.error("Failure! Stopping MQTT client")
            self._client.stop()
            return EXIT_FAILURE
        return EXIT_SUCCESS


def load_config():
    try:
        with open(CONFIG_FILEPATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    setup_logging()

    parser = argparse.ArgumentParser(
        description="wb-mqtt-shtyl - UPS monitoring service"
    )
    parser.add_argument("--port", help="Serial port")
    parser.add_argument("--broker", help="MQTT broker URL")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    args = parser.parse_args(argv)

    logging.getLogger().setLevel(getattr(logging, args.log_level))

    config = load_config()

    ups_type = config.get("type", "shtyl")
    if ups_type not in PARSERS:
        LOGGER.error(
            f"Unknown UPS type: {ups_type}. Supported: {', '.join(PARSERS.keys())}"
        )
        return EXIT_CONFIG_ERROR

    serial_port = args.port or config.get("port", "/dev/ttyUSB0")
    broker_url = args.broker or config.get("broker", "tcp://localhost:1883")

    serial_port = args.port or config.get("port", "COM7")
    broker_url = args.broker or config.get("broker", "tcp://172.16.4.175:1883")

    LOGGER.info(f"Starting wb-mqtt-shtyl service (type={ups_type}, port={serial_port})")

    service = UPSService(
        ups_type=ups_type, serial_port=serial_port, broker_url=broker_url
    )
    return service.run()


if __name__ == "__main__":
    sys.exit(main())
