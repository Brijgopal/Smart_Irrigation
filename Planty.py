#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import Adafruit_DHT
from gpiozero import LED, Button
from time import sleep

import pubnub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNOperationType, PNStatusCategory

pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-c823b87a-2007-4df2-88da-ad535587f882'
pnconfig.subscribe_key = 'sub-c-4143a002-4a53-11e9-bc27-728c10c631fc'
pnconfig.ssl = False
pubnub = PubNub(pnconfig)

# Pump is connected to GPIO4 as an LED
pump = LED(4)

# DHT Sensor is connected to GPIO17
sensor = 11
pin = 17

# Soil Moisture sensor is connected to GPIO14 as a button
soil = Button(14)

cmd = -1
TVal = -1
HVal = -1
pump.on()

class MySubscribeCallback(SubscribeCallback):

    def status(self, pubnub, status):
        pass

    def presence(self, pubnub, presence):
        pass

    def message(self, pubnub, message):

        global cmd, TVal, HVal
        if message.message['cmd'] == 'ON':
            cmd = 1
            TVal = message.message['TVal']
            HVal = message.message['HVal']

        elif message.message['cmd'] == 'OFF':
            cmd = 0

        elif message.message['cmd'] == 'WATER':
            cmd = 2

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('ch1').execute()


def publish_callback(result, status):
    pass


def soil_Status():
    if soil.is_held:
        print('Wet soil detected')
        return False
    else:
        print('Dry soil detected')
        return True


while True:
    
    (humidity, temperature) = Adafruit_DHT.read_retry(sensor, pin)
    DHTVal = 'Temp={0:0.1f}*C\tHumidity={1:0.1f}%\t'.format(temperature,humidity)

    if cmd == 1:

        dictionary = {'eon': {'Temperature': temperature, 'Humidity': humidity}}
        pubnub.publish().channel('ch2').message(DHTVal).pn_async(publish_callback)
        pubnub.publish().channel("eon-chart").message(dictionary).pn_async(publish_callback)
        
        print(DHTVal),
        dry = soil_Status()
        if dry == True and (humidity<HVal or temperature>TVal):
            print('\t\tPump ---> ON')
            pump.off()
            sleep(5)
            print('\t\tPump ---> OFF')
            pump.on()
            sleep(1)
        else:
            pump.on()
            sleep(1)
            
    elif cmd == 2:

        print(DHTVal)
        dictionary = {'eon': {'Temperature': temperature, 'Humidity': humidity}}
        pubnub.publish().channel('ch2').message(DHTVal).pn_async(publish_callback)
        pubnub.publish().channel("eon-chart").message(dictionary).pn_async(publish_callback)
        pump.off()
        sleep(5)
        pump.on()
        cmd = 0
    
    else:
        pump.on()
        sleep(3)
        