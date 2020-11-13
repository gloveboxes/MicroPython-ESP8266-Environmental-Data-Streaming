# Streaming Data from ESP8266 using MicroPython and MQTT

## Resources 

* [MicroPython](https://micropython.org/)
* [MicroPython Online Simulator](https://micropython.org/unicorn/)
* [MicroPython libraries](https://github.com/micropython/micropython-lib)
* [MicroPython PiP Package Index](https://pypi.python.org/pypi?%3Aaction=search&term=micropython)
* [ESP8266 Documentation](http://docs.micropython.org/en/latest/esp8266/)
* [ESP8266 Firmware](http://micropython.org/download/#esp8266)
* [ESP8266 Firmware Tutorial](http://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html#deploying-the-firmware)
* [Adafruit MicroPython Resources](https://www.google.com.au/search?client=ubuntu&hs=h2P&channel=fs&q=adafruit+micropython&spell=1&sa=X&ved=0ahUKEwii1ITmhpDVAhUEXrwKHY3YDoUQvwUIIygA&biw=1221&bih=626)


### Other

* [MicroPython BME280 Sensor Driver](https://github.com/catdog2/mpy_bme280_esp8266/blob/master/bme280.py)
* [MicroPython SHT30 Sensor Driver](https://github.com/rsc1975/micropython-sht30)
* [Espressif esptool](https://github.com/espressif/esptool)
* [Mosquitto Broker](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-16-04)
* [PuTTY](http://www.putty.org/)
* [Serial Support on the Windows Subsystem for Linux](https://blogs.msdn.microsoft.com/wsl/2017/04/14/serial-support-on-the-windows-subsystem-for-linux/?WT.mc_id=iot-0000-dglover)


### Overview of ESP8266 flashing process

1. Install esptool
2. Erase Flash
3. Deploy MicroPython Firmware

See [Flashing MicroPython Flasing How-to Tutorial](http://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html#deploying-the-firmware)



## MicroPython and Publish over MQTT

Deploy the solution to the ESP8266 MicroPython flash as follows.

See [Adafruit MicroPython Tool (ampy)](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy) for information on copying files to the ESP32.

```bash
pip install adafruit-ampy

ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put config.py

ampy --port /dev/ttyUSB0 put bme280.py
ampy --port /dev/ttyUSB0 put sht30.py

ampy --port /dev/ttyUSB0 put config_default.json

ampy --port /dev/ttyUSB0 put sensor_bme280.py
ampy --port /dev/ttyUSB0 put sensor_sht30.py
ampy --port /dev/ttyUSB0 put sensor_fake.py
```

```python
# boot.py

import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("Wifi SSID", "Wifi password")
```



```python
# main.py

# http://docs.micropython.org/en/latest/esp8266/index.html
# http://garybake.com/wemos-oled-shield.html
# http://docs.micropython.org/en/latest/esp8266/esp8266/quickref.html#adc-analog-to-digital-conversion

from umqtt.robust import MQTTClient
from machine import I2C, Pin
import utime as time
import gc
import ssd1306 as oled
from machine import ADC
import esp
import config


# Wifi connect established in the boot.py file. Uncomment if needed
# import network
# sta_if = network.WLAN(network.STA_IF)
# sta_if.active(True)


#upip packages - see README.md
# upip.install('micropython-umqtt.simple')
# upip.install('micropython-umqtt.robust')

BuiltinLedPin = 2

cfg = config.Config('config_default.json')

sta_if.connect(cfg.wifiSsid, cfg.wifiPwd)
client = MQTTClient(str(esp.flash_id()), cfg.mqttBroker)
mySensor = cfg.sensor.Sensor()

builtinLed = Pin(BuiltinLedPin, Pin.OUT)
adc = ADC(0)            # create ADC object on ADC pin
i2c = I2C(scl=Pin(5), sda=Pin(4)) 

esp.sleep_type(esp.SLEEP_LIGHT)


def initDisplay(i2c):
    i2cDevices = I2C.scan(i2c)
    if 0x3c in i2cDevices:
        display = oled.SSD1306_I2C(64, 48, i2c)
        return True
    else:        
        print('No OLED Display found')
        return False

def initialise():
    blinkcnt = 0
    checkwifi()
    while blinkcnt < 50:
        builtinLed.value(blinkcnt % 2)
        blinkcnt = blinkcnt + 1
        time.sleep_ms(100)

def checkwifi():
    blinkcnt = 0
    while not sta_if.isconnected():
        time.sleep_ms(500)
        builtinLed.value(blinkcnt % 2)
        blinkcnt = blinkcnt + 1

def setContrast():
    lightlevel = adc.read()
    if lightlevel < 200:
        return 0
    if lightlevel < 600:
        return 100
    return 255

def publish():
    count = 1
    while True:
        builtinLed.value(0)
        checkwifi()
        
        temperature, pressure, humidity = mySensor.measure()

        freeMemory = gc.mem_free()

        if oledDisplay:
            display.fill(0)
            display.contrast(setContrast())
            display.text(v[0], 0, 0)
            display.text(v[1], 0, 10)
            display.text(v[2], 0, 20)
            display.text(str(freeMemory), 0, 30)
            display.text(str(count), 0, 40)
            display.show()    

        msg = b'{"DeviceId":"%s",MsgId":%u,"Mem":%u,"Celsius":%s,"Pressure":%s,"Humidity":%s}' % (cfg.deviceId, count, freeMemory, temperature, pressure, humidity)
        client.publish(b"home/weather/%s" % cfg.deviceId, msg)

        builtinLed.value(1)
        count = count + 1
        
        time.sleep(cfg.sampleRate)


oledDisplay = initDisplay(i2c)

initialise()

client.reconnect()

publish()

```

## Connecting to ESP32 with Putty

Install Putty for your platform. Connect at 115200 baud rate

See [Adafruit Serial REPL Tutorial](https://learn.adafruit.com/micropython-basics-how-to-load-micropython-on-a-board/serial-terminal).
