from serial import Serial


class UpsParser:
    device_id = "shtyl_ups"
    controls = []
    state_keys = []

    def parse(self, data: bytes) -> dict:
        raise NotImplementedError

    def get_command(self) -> bytes:
        raise NotImplementedError

    def test_connection(self, serial_port: Serial) -> bool:
        raise NotImplementedError
