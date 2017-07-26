ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put config.py

ampy --port /dev/ttyUSB0 put bme280.py
ampy --port /dev/ttyUSB0 put sht30.py

ampy --port /dev/ttyUSB0 put config.json

ampy --port /dev/ttyUSB0 put sensor_bme280.py
ampy --port /dev/ttyUSB0 put sensor_sht30.py
ampy --port /dev/ttyUSB0 put sensor_fake.py