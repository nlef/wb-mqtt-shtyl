# wb-mqtt-shtyl

MQTT-сервис для мониторинга ИБП Штиль и совместимых ИБП через последовательный порт по стандарту rs-232.

## Поддерживаемые протоколы взаимодействия с ИБП 

- **shtyl** — ИБП Штиль с протоколом Shtyl (14400 baud)
- **megatec** — ИБП с протоколом Megatec (2400 baud, XON/XOFF)

## Подключение

Подключите ИБП с использованием карты `IC-RS232/Dry contacts` к USB-порту Wiren Board или с использованием модуля `WBE2-I-RS232`. Укажите соотвествующий последовательный порт (например `/dev/ttyUSB0`) в конигурационном файле сервиса.

## Конфигурация

В файле `/etc/wb-mqtt-shtyl.conf`:

```json
{
  "type": "shtyl",
  "port": "/dev/ttyUSB0",
  "broker": "tcp://localhost:1883",
  "log_level": "INFO"
}
```

Параметры:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| type | Тип протокола ИБП: `shtyl` или `megatec` | `shtyl` |
| port | Последовательный порт | `/dev/ttyUSB0` |
| broker | URL MQTT брокера | `tcp://localhost:1883` |
| log_level | Уровень логирования: `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

## Запуск из командной строки

```bash
wb-mqtt-shtyl --port /dev/ttyUSB0 --broker tcp://localhost:1883
```

## Управление сервисом

```bash
systemctl enable wb-mqtt-shtyl
systemctl start wb-mqtt-shtyl
systemctl status wb-mqtt-shtyl
```

## Публикуемые параметры MQTT

Устройство: `/devices/shtyl_ups/`

| Параметр | Тип | Описание | Shtyl | Megatec |
|----------|-----|---------|:------:|:-------:|
| input_voltage | voltage | Входное напряжение (В) | + | + |
| input_frequency | value (Hz) | Входная частота (Гц) | + | + |
| output_voltage | voltage | Выходное напряжение (В) | + | + |
| output_frequency | value (Hz) | Выходная частота (Гц) | + | - |
| output_load | value (%) | Нагрузка (%) | + | + |
| battery_voltage | voltage | Напряжение батареи (В) | + | + |
| battery_current | value (A) | Ток батареи (А) | + | - |
| battery_temperature | temperature | Температура батареи (°C) | + | - |
| controller_temperature | temperature | Температура контроллера (°C) | + | - |
| radiator_temperature | temperature | Температура радиатора (°C) | + | - |
| time_remaining | value (s) | Оставшееся время работы (с) | + | - |
| temperature | temperature | Температура (°C) | - | + |
| alerts | text | Текущие уведомления | + | - |

## Сборка deb-пакета

```bash
dpkg-buildpackage -rfakeroot -us -uc
```

## Соответствие стандартам

Сервис соответствует [Wiren Board Software Conventions](https://github.com/wirenboard/conventions).
