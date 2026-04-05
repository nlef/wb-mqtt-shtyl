import logging

import serial
from serial import Serial

from .base import UpsParser

LOGGER = logging.getLogger(__name__)

IQ15_MULTIPLIER = 1.0 / pow(2.0, 15.0)


def iq15(buffer, start, mult=1.0):
    return (
            int.from_bytes(buffer[start: start + 2], byteorder="little", signed=True)
            * IQ15_MULTIPLIER
            * mult
    )


def iq15_round(buffer, start, mult=1.0):
    return round(iq15(buffer, start, mult), 2)


def u16(buffer, start, mult=1):
    return (
            int.from_bytes(buffer[start: start + 2], byteorder="little", signed=False)
            * mult
    )


def u64(buffer, start):
    return int.from_bytes(buffer[start: start + 8], byteorder="little", signed=False)


def get_alarm(value, bit):
    return (value >> bit) & 1


ALERT_NAMES_RU = {
    "general_fault": "Общая ошибка",
    "overload": "Перегрузка",
    "output_short_circuit": "Короткое замыкание на выходе",
    "low_load_impedance": "Низкий импеданс нагрузки",
    "overheat": "Перегрев",
    "power_supply_absent": "Отсутствует источник питания",
    "intermediate_overvoltage": "Промежуточное перенапряжение",
    "capacity_not_charging": "Батарея не заряжается",
    "aux_power_supply_fault": "Ошибка вспомогательного питания",
    "output_relay_sticking": "Залипание реле выхода",
    "converter_sync_timeout": "Таймаут синхронизации конвертера",
    "converter_not_sync_with_grid": "Конвертер не синхронизирован с сетью",
    "converter_not_sync_with_bypass": "Конвертер не синхронизирован с байпасом",
    "converter_fan_fault": "Ошибка вентилятора конвертера",
    "temperature_probe_fault": "Ошибка датчика температуры",
    "intermediate_undervoltage": "Промежуточное пониженное напряжение",
    "parallel_synchronization_failure": "Ошибка параллельной синхронизации",
    "inverter_output_abnormal": "Аномальный выход инвертора",
    "grid_overvoltage": "Перенапряжение сети",
    "grid_undervoltage": "Пониженное напряжение сети",
    "grid_low_quality_voltage": "Низкое качество напряжения сети",
    "grid_low_quality_frequency": "Низкое качество частоты сети",
    "grid_phase_overvoltage": "Перенапряжение фазы сети",
    "grid_phase_undervoltage": "Пониженное напряжение фазы сети",
    "grid_phase_low_quality_voltage": "Низкое качество напряжения фазы сети",
    "grid_neutral_breakage": "Обрыв нуля сети",
    "grid_invalid_phase_order": "Неправильный порядок фаз сети",
    "bypass_overvoltage": "Перенапряжение байпаса",
    "bypass_undervoltage": "Пониженное напряжение байпаса",
    "bypass_low_quality_voltage": "Низкое качество напряжения байпаса",
    "bypass_low_quality_frequency": "Низкое качество частоты байпаса",
    "bypass_phase_overvoltage": "Перенапряжение фазы байпаса",
    "bypass_phase_undervoltage": "Пониженное напряжение фазы байпаса",
    "bypass_phase_low_quality": "Низкое качество фазы байпаса",
    "bypass_neutral_breakage": "Обрыв нуля байпаса",
    "bypass_overload": "Перегрузка байпаса",
    "bypass_short_circuit": "Короткое замыкание байпаса",
    "bypass_low_load_impedance": "Низкий импеданс нагрузки байпаса",
    "bypass_overheat": "Перегрев байпаса",
    "bypass_output_relay_sticking": "Залипание реле выхода байпаса",
    "battery_absent": "Батарея отсутствует",
    "battery_needs_replace": "Батарею необходимо заменить",
    "battery_overheat": "Перегрев батареи",
    "battery_critical_overheat": "Критический перегрев батареи",
    "battery_overvoltage": "Перенапряжение батареи",
    "battery_charger_overheat": "Перегрев зарядного устройства",
    "battery_charger_low_input_power": "Низкая мощность входа зарядного",
    "battery_charger_intermediate_undervoltage": "Промежуточное пониженное напряжение зарядного",
    "battery_charger_input_undervoltage": "Пониженное напряжение входа зарядного",
    "battery_charger_general_fault": "Общая ошибка зарядного",
    "settings_io_fault": "Ошибка настроек ввода-вывода",
    "emergency_power_off_fault": "Аварийное отключение",
    "power_critical_fault": "Критическая ошибка питания",
}


def get_alerts_string(alerts: dict) -> str:
    return ", ".join(
        ALERT_NAMES_RU[name] for name, value in alerts.items() if value == 1
    )


class ShtylParser(UpsParser):
    device_id = "shtyl_ups"
    state_keys = [
        "input_voltage",
        "input_frequency",
        "output_voltage",
        "output_frequency",
        "controller_temperature",
        "radiator_temperature",
        "time_remaining",
        "output_load",
        "battery_temperature",
        "battery_voltage_target",
        "battery_voltage",
        "battery_current",
        "battery_state",
        "alerts",
    ]
    controls = [
        (
            "alerts",
            {
                "order": 0,
                "title": {"en": "Alerts", "ru": "Уведомления"},
                "readonly": True,
                "type": "text",
            },
        ),
        (
            "input_voltage",
            {
                "order": 1,
                "title": {"en": "Input voltage", "ru": "Входное напряжение"},
                "precision": 0.1,
                "readonly": True,
                "type": "voltage",
            },
        ),
        (
            "input_frequency",
            {
                "order": 2,
                "title": {"en": "Input frequency", "ru": "Входная частота"},
                "precision": 0.1,
                "readonly": True,
                "type": "value",
                "units": "Hz",
            },
        ),
        (
            "output_voltage",
            {
                "order": 3,
                "title": {"en": "Output voltage", "ru": "Выходное напряжение"},
                "precision": 0.1,
                "readonly": True,
                "type": "voltage",
            },
        ),
        (
            "output_frequency",
            {
                "order": 4,
                "title": {"en": "Output frequency", "ru": "Выходная частота"},
                "precision": 0.1,
                "readonly": True,
                "type": "value",
                "units": "Hz",
            },
        ),
        (
            "battery_state",
            {
                "order": 5,
                "title": {"en": "Battery state", "ru": "Статус батареи"},
                "readonly": True,
                "type": "value",
            },
        ),
        (
            "battery_voltage_target",
            {
                "order": 6,
                "title": {"en": "Battery target voltage", "ru": "Напряжение батареи целевое"},
                "readonly": True,
                "type": "voltage",
            },
        ),
        (
            "battery_voltage",
            {
                "order": 7,
                "title": {"en": "Battery voltage", "ru": "Напряжение батареи"},
                "precision": 0.1,
                "readonly": True,
                "type": "voltage",
            },
        ),
        (
            "battery_current",
            {
                "order": 8,
                "title": {"en": "Battery current", "ru": "Ток батареи"},
                "precision": 0.1,
                "readonly": True,
                "type": "current",
            },
        ),

        (
            "controller_temperature",
            {
                "order": 9,
                "title": {
                    "en": "Controller temperature",
                    "ru": "Температура контроллера",
                },
                "precision": 0.1,
                "readonly": True,
                "type": "temperature",
            },
        ),
        (
            "radiator_temperature",
            {
                "order": 10,
                "title": {"en": "Radiator temperature", "ru": "Температура радиатора"},
                "precision": 0.1,
                "readonly": True,
                "type": "temperature",
            },
        ),
        (
            "battery_temperature",
            {
                "order": 11,
                "title": {"en": "Battery temperature", "ru": "Температура батареи"},
                "type": "temperature",
            },
        ),
        (
            "time_remaining",
            {
                "order": 12,
                "title": {"en": "Time remaining", "ru": "Оставшееся время работы"},
                "readonly": True,
                "type": "value",
                "units": "s",
            },
        ),
        (
            "output_load",
            {
                "order": 13,
                "title": {"en": "Output load", "ru": "Выходная нагрузка"},
                "readonly": True,
                "type": "value",
                "units": "%",
            },
        ),
    ]

    def get_command(self) -> bytes:
        return b"\xaa\x55\x01\x01\x0a\x00\x00\x04\x1e\x5e"

    def test_connection(self, serial_port: Serial) -> bool:
        LOGGER.debug("Testing Shtyl connection...")
        command = b"\xaa\x55\x01\x01\x0a\x00\x00\x01\xc3\x94"
        try:
            serial_port.write(command)
            res = serial_port.readall()
            return res != b""
        except serial.SerialException:
            LOGGER.exception("Serial exception")
            return False

    def parse(self, data: bytes) -> dict:

        voltage_phaze = [iq15_round(data, 8 + i * 2, 1000) for i in range(3)]
        curr_phaze = [iq15_round(data, 14 + i * 2, 100) for i in range(3)]
        bypass_voltage_phaze = [iq15_round(data, 20 + i * 2, 1000) for i in range(3)]
        out_voltage_phaze = [iq15_round(data, 26 + i * 2, 1000) for i in range(3)]
        out_curr_active_phaze = [iq15_round(data, 32 + i * 2, 100) for i in range(3)]
        out_curr_total_phaze = [iq15_round(data, 38 + i * 2, 100) for i in range(3)]

        in_freq_phaze_0 = iq15_round(data, 44, 100)
        bypass_freq_phaze_0 = iq15_round(data, 46, 100)
        out_freq_phaze_0 = iq15_round(data, 48, 100)

        controller_temp = iq15_round(data, 50, 1000)
        radiator_temp = iq15_round(data, 52, 1000)
        vab_float = iq15_round(data, 54, 1000)

        vab_pos = iq15_round(data, 56, 1000)
        vab_neg = iq15_round(data, 58, 1000)
        iab_pos = iq15_round(data, 60, 100)
        iab_neg = iq15_round(data, 62, 100)
        p_ab = iq15_round(data, 64, 1000)

        t_remaining = u16(data, 66, 60000)

        state_long = u64(data, 68)
        state_bits = {
            "emergency_power_off_state": (state_long >> 0) & 7,
            "bypass_mode": (state_long >> 3) & 7,
            "battery_usage_mode": (state_long >> 6) & 7,
            "battery_charger_state": (state_long >> 9) & 7,
            "battery_state": (state_long >> 12) & 7,
            "bypass_grid_state": (state_long >> 19) & 7,
            "rectifier_grid_state": (state_long >> 16) & 7,
            "battery_transfer_controller_state": (state_long >> 22) & 7,
            "inverter_input_source": (state_long >> 25) & 7,
            "power_factor_corrector_state": (state_long >> 28) & 7,
            "dc_dc_power_supply_state": (state_long >> 32) & 7,
            "inverter_state": (state_long >> 35) & 7,
            "inverter_master_oscillator_state": (state_long >> 38) & 7,
            "bypass_state": (state_long >> 41) & 7,
            "output_state": (state_long >> 44) & 7,
            "load_state": [(state_long >> 48) & 7, (state_long >> 51) & 7],
        }

        alert_long = u64(data, 76)
        alert_bits = {
            "general_fault": 0,
            "overload": 1,
            "output_short_circuit": 2,
            "low_load_impedance": 3,
            "overheat": 4,
            "power_supply_absent": 5,
            "intermediate_overvoltage": 6,
            "capacity_not_charging": 7,
            "aux_power_supply_fault": 8,
            "output_relay_sticking": 9,
            "converter_sync_timeout": 10,
            "converter_not_sync_with_grid": 11,
            "converter_not_sync_with_bypass": 12,
            "converter_fan_fault": 13,
            "temperature_probe_fault": 14,
            "intermediate_undervoltage": 15,
            "parallel_synchronization_failure": 16,
            "inverter_output_abnormal": 17,
            "grid_overvoltage": 18,
            "grid_undervoltage": 19,
            "grid_low_quality_voltage": 20,
            "grid_low_quality_frequency": 21,
            "grid_phase_overvoltage": 22,
            "grid_phase_undervoltage": 23,
            "grid_phase_low_quality_voltage": 24,
            "grid_neutral_breakage": 25,
            "grid_invalid_phase_order": 26,
            "bypass_overvoltage": 30,
            "bypass_undervoltage": 31,
            "bypass_low_quality_voltage": 32,
            "bypass_low_quality_frequency": 33,
            "bypass_phase_overvoltage": 34,
            "bypass_phase_undervoltage": 35,
            "bypass_phase_low_quality": 36,
            "bypass_neutral_breakage": 37,
            "bypass_overload": 38,
            "bypass_short_circuit": 39,
            "bypass_low_load_impedance": 40,
            "bypass_overheat": 41,
            "bypass_output_relay_sticking": 42,
            "battery_absent": 46,
            "battery_needs_replace": 47,
            "battery_overheat": 48,
            "battery_critical_overheat": 49,
            "battery_overvoltage": 50,
            "battery_charger_overheat": 53,
            "battery_charger_low_input_power": 54,
            "battery_charger_intermediate_undervoltage": 55,
            "battery_charger_input_undervoltage": 56,
            "battery_charger_general_fault": 57,
            "settings_io_fault": 60,
            "emergency_power_off_fault": 61,
            "power_critical_fault": 63,
        }
        alerts = {name: get_alarm(alert_long, bit) for name, bit in alert_bits.items()}

        pload = iq15_round(data, 84, 1000)
        out_load_percent_phaze = [iq15_round(data, 86 + i * 2, 1000) for i in range(3)]

        last_time_on_batery = u16(data, 92, 1000)
        battery_temp = iq15_round(data, 94, 1000)

        full_ress = {
            "voltage_phaze": voltage_phaze,
            "curr_phaze": curr_phaze,
            "bypass_voltage_phaze": bypass_voltage_phaze,
            "out_voltage_phaze": out_voltage_phaze,
            "out_curr_active_phaze": out_curr_active_phaze,
            "out_curr_total_phaze": out_curr_total_phaze,
            "in_freq_phaze_0": in_freq_phaze_0,
            "bypass_freq_phaze_0": bypass_freq_phaze_0,
            "out_freq_phaze_0": out_freq_phaze_0,
            "controller_temp": controller_temp,
            "radiator_temp": radiator_temp,
            "vab_float": vab_float,
            "vab_pos": vab_pos,
            "vab_neg": vab_neg,
            "iab_pos": iab_pos,
            "iab_neg": iab_neg,
            "p_ab": p_ab,
            "t_remaining": t_remaining,
            "state_bits": state_bits,
            "alerts": alerts,
            "pload": pload,
            "out_load_percent_phaze": out_load_percent_phaze,
            "last_time_on_batery": last_time_on_batery,
            "battery_temperature": battery_temp,
        }
        LOGGER.debug(f"full_ress: {full_ress}")

        return {
            "input_voltage": voltage_phaze[0],
            "input_frequency": in_freq_phaze_0,
            "output_voltage": iq15_round(data, 26, 1000),
            "output_frequency": out_freq_phaze_0,
            "controller_temperature": controller_temp,
            "radiator_temperature": radiator_temp,
            "time_remaining": t_remaining,
            "output_load": out_load_percent_phaze[0],
            "battery_temperature": battery_temp,
            "battery_voltage_target": vab_float,
            "battery_voltage": vab_pos,
            "battery_current": iab_pos,
            "battery_state": state_bits["battery_state"],
            "alerts": get_alerts_string(alerts),
        }
