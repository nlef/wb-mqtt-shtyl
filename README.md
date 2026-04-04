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
  "broker": "tcp://localhost:1883"
}
```

Параметры:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| type | Тип протокола ИБП: `shtyl` или `megatec` | `shtyl` |
| port | Последовательный порт | `/dev/ttyUSB0` |
| broker | URL MQTT брокера | `tcp://localhost:1883` |

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

| Параметр | Описание | Shtyl | Megatec |
|----------|----------|-------|---------|
| input_voltage | Входное напряжение (В) | + | + |
| input_frequency | Входная частота (Гц) | + | + |
| output_voltage | Выходное напряжение (В) | + | + |
| output_frequency | Выходная частота (Гц) | + | - |
| output_load | Нагрузка (%) | + | + |
| battery_voltage | Напряжение батареи (В) | + | + |
| battery_temperature | Температура батареи (°C) | + | - |
| controller_temperature | Температура контроллера (°C) | + | - |
| radiator_temperature | Температура радиатора (°C) | + | - |
| time_remaining | Оставшееся время работы (с) | + | - |
| temperature | Температура (°C) | - | + |
| alerts | Текущие уведомления | + | - |

## Сборка deb-пакета

```bash
dpkg-buildpackage -rfakeroot -us -uc
```
