from umqtt.simple import MQTTClient
import influxdb

class Sensor:
    def __init__(self, name, server, port, keyfile, certfile, root_topic):

        self.topic = root_topic + '/' + name

        with open(keyfile, 'rb') as f:
            key = f.read()

        with open(certfile, 'rb') as f:
            cert = f.read()

        self.client = MQTTClient(name,
                                server=server,
                                port=port,
                                ssl=True,
                                ssl_params={ 'key': key, 'cert': cert},
                                keepalive=60)

    def connect(self):
        self.client.set_last_will(self.topic + '/status', b'offline', retain=True, qos=1)
        self.client.connect()

        self.publish_status(b'online')


    def disconnect(self):
        self.publish_status(b'offline')
        self.client.disconnect()

    def publish(self, topic, data):
        self.client.publish(topic, data)

    def publish_measurment(self, measurment):
        topic = self.topic + '/measurement'
        data = measurment.to_line_protocol()

        self.publish(topic, data)
        print('Published {} = {}'.format(topic, data))

    def publish_status(self, status):
        self.client.publish(self.topic + '/status', status, retain=True, qos=1)