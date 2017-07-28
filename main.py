# http://docs.micropython.org/en/latest/esp8266/index.html
# http://garybake.com/wemos-oled-shield.html
# http://docs.micropython.org/en/latest/esp8266/esp8266/quickref.html#adc-analog-to-digital-conversion

from umqtt.robust import MQTTClient
from machine import I2C, Pin, ADC
import ssd1306 as oled
import utime as time
import esp
import gc
import config



# Wifi connect established in the boot.py file. Uncomment if needed
# import network
# sta_if.active(True)


# upip packages - see README.md
# upip.install('micropython-umqtt.simple')
# upip.install('micropython-umqtt.robust')

ap_if = network.WLAN(network.AP_IF) # turn off the access point which is on by default
ap_if.active(False)


cfg = config.Config('config.json')

if cfg.isEsp8266:
    BuiltinLedPin = 2
    i2c = I2C(scl=Pin(5), sda=Pin(4))
    adc = ADC(0)            # create ADC object on ADC pin
    mqttId = str(esp.flash_id())
    esp.sleep_type(esp.SLEEP_LIGHT)
else:
    BuiltinLedPin = 5
    i2c = I2C(scl=Pin(22), sda=Pin(21))
    adc = None
    import urandom as random
    mqttId = str(random.randint(100,100000))



builtinLed = Pin(BuiltinLedPin, Pin.OUT)

mySensor = cfg.sensor.Sensor(i2c)

client = MQTTClient(mqttId, cfg.mqttBroker)
sta_if.connect(cfg.wifiSsid, cfg.wifiPwd)

display = None


def initDisplay(i2c):
    global display, adc
    i2cDevices = I2C.scan(i2c)
    if 60 in i2cDevices:
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
    if adc == None:
        return 255
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
            display.text(temperature, 0, 0)
            display.text(pressure, 0, 10)
            display.text(humidity, 0, 20)
            display.text(str(freeMemory), 0, 30)
            display.text(str(count), 0, 40)
            display.show()

        msg = b'{"DeviceId":"%s","MsgId":%u,"Mem":%u,"Celsius":%s,"Pressure":%s,"Humidity":%s}' % (
            cfg.deviceId, count, freeMemory, temperature, pressure, humidity)
        client.publish(b"home/weather/%s" % cfg.deviceId, msg)

        builtinLed.value(1)
        count = count + 1

        time.sleep(cfg.sampleRate)


oledDisplay = initDisplay(i2c)

initialise()

client.reconnect()

publish()
