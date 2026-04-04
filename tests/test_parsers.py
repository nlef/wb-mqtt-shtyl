from wb_mqtt_shtyl.protocols import PARSERS, SERIAL_SETTINGS


def test_parsers_registered():
    assert "shtyl" in PARSERS
    assert "megatec" in PARSERS


def test_serial_settings_registered():
    assert "shtyl" in SERIAL_SETTINGS
    assert "megatec" in SERIAL_SETTINGS
