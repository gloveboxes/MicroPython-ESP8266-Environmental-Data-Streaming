from sht30 import SHT30


class Sensor():

    def __init__(self, i2c):
        self.sht = SHT30()

    def measure(self):
        temperature, humidity = self.sht.measure()
        pressure = 1010

        return (temperature, pressure, humidity)
