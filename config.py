import json


class Config():

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
            self.isEsp8266 = True
            if config.get('IsESP8266') and config['IsESP8266'] == 'False':
                self.isEsp8266 = False 

        except:
            print('Error loading config data')

    def __init__(self, configFile):
        self.config_load(configFile)
