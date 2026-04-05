from setuptools import find_packages, setup


def get_version():
    with open("debian/changelog", encoding="utf-8") as f:
        return f.readline().split()[1][1:-1].split("~")[0]


setup(
    name="wb-mqtt-shtyl",
    version=get_version(),
    maintainer="nlef",
    description="MQTT service for monitoring Shtyl UPS",
    url="https://github.com/nlef/wb-mqtt-shtyl",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "wb-mqtt-shtyl=wb_mqtt_shtyl.main:main",
        ],
    },
    license="MIT",
)
