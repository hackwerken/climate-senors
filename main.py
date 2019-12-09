import network
import dht12
import time
import machine
import esp
import mqtt
import ujson
import influxdb

config = ujson.loads(open('config.json').read())

from machine import I2C, Pin, Signal
i2c = I2C(scl=Pin(5), sda=Pin(4))
sensor = dht12.DHT12(i2c)

ledPin = machine.Pin(2, machine.Pin.OUT)
led = Signal(ledPin, invert=True)

sta_if = network.WLAN(network.STA_IF)

def togleLed():
    led.value(not led.value())

def scan():
    scan = sta_if.scan()
    for scanned in scan:
        for config_network in config['networks']:
            if scanned[0].decode() == config_network[0]:
                return (config_network[0], config_network[1])
    return None

def do_conncect():
    issd, password = scan()
    print('Connecting to:', issd)
    sta_if.connect(issd, password) 

def connect():
    if not sta_if.isconnected():
        sta_if.active(True)
        do_conncect()

        count = 0;
        while not sta_if.isconnected():
            togleLed()
            time.sleep_ms(100)

            count += 1
            if count >= 100:
                count = 0
                do_conncect()

    led.off()
    print('network config:', sta_if.ifconfig())

    import webrepl
    import gc
    webrepl.start()
    gc.collect()

def send():
    led.on()
    
    client = mqtt.Sensor(name=config['meta']['id'],
                         server=config['mqtt']['server'],
                         port=config['mqtt']['port'],
                         keyfile=config['mqtt']['key_file'],
                         certfile=config['mqtt']['cert_file'],
                         root_topic=config['mqtt']['root_topic'])

    client.connect()
    print('Connected to MQTT broker')

    measurement = influxdb.Measurement('climate')
    measurement.tags = {'location' : 'woonkamer',
                        'id': 'bureau'}
    measurement.fields = {'temperature' : sensor.temperature(), 
                          'humidity': sensor.humidity()}

    client.publish_measurment(measurement)

    client.disconnect()
        
    led.off()


def main():
    try:
        network.WLAN(network.AP_IF).active(False)
        
        connect()
        
        while True:
            sensor.measure()
            send()
            #time.sleep(10)
            break
        
        time.sleep_ms(100)

        # give us some time to reprogram
        if(machine.reset_cause() != machine.DEEPSLEEP_RESET):
             for x in range(10):
                togleLed()
                time.sleep_ms(100)
                togleLed()
                time.sleep_ms(500)
           
        print('Entering deepsleep')
        micro = 1000000
        esp.deepsleep(5 * 60 * micro)



    except Exception as e:
        from sys import print_exception
        print_exception(e)

        for x in range(10):
            togleLed()
            time.sleep(1)

        machine.reset()


if __name__ == '__main__':
    main()
