from umqtt.simple import MQTTClient

class Sensor:
    def __init__(self, name, server, port, keyfile, certfile, root_topic):

        self.topic = root_topic + '/' + name
        self.repl = None
        self.on_repl_disabled = None

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
        self.client.set_callback(self._subscribe_callback)
        
        self.client.set_last_will(self.topic + '/status', b'offline', retain=True, qos=1)
        self.client.connect()

        self.publish_status(b'online')

        self.client.subscribe(self.topic + '/repl')
        self.client.wait_msg()

    def disconnect(self):
        self.publish_status(b'offline')
        self.client.disconnect()

    def publish(self, topic, data):
        t = self.topic + '/' + topic
        self.client.publish(t, data)
        print('Published {} = {}'.format(topic, data))

    def update(self):
        self.client.ping()
        self.client.wait_msg()

    def publish_measurment(self, measurment):
        data = measurment.to_line_protocol()
        self.publish('measurement', data)

    def publish_status(self, status):
        self.client.publish(self.topic + '/status', status, retain=True, qos=1)

    def _subscribe_callback(self, topic, msg):
        print('Received: ', topic, msg)

        if topic.decode() == self.topic + '/repl':
            
            prev = self.repl
            self.repl = (msg == b'1')
            
            if self.on_repl_disabled:
                if prev and not self.repl:
                    self.on_repl_disabled()

