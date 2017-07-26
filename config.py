import json

class Config():

    @property
    def sampleRateInSeconds(self):
        return self._sampleRate

    @sampleRateInSeconds.setter
    def sampleRateInSeconds(self, value):
        self._sampleRate = float(value)

    def config_defaults(self):
        print('Loading default config settings')

        self.sensor = __import__('sensor_fake') 
        self.deviceId = 'default'
        self.sampleRate = 60


    def config_load(self, configFile):
        #global sensor, hubAddress, deviceId, sharedAccessKey, owmApiKey, owmLocation
        try:
            print('Loading {0} settings'.format(configFile))

            config_data = open(configFile)
            config = json.load(config_data)

            self.sensor = __import__(config['SensorModule']) 
            self.deviceId = config['DeviceId']
            self.sampleRate = config['SampleRate']
            self.mqttBroker = config['MqttBroker']
            self.wifiSsid = config['WifiSsid']
            self.wifiPwd = config['WifiPwd']

        except:
            self.config_defaults()

    def __init__(self, configFile):
        self.config_load(configFile)