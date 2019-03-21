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
pnconfig.subscribe_key = ""
pnconfig.publish_key = ""
pnconfig.ssl = False
 
pubnub = PubNub(pnconfig)

#Pump is connected to GPIO4 as an LED
pump = LED(4)

#DHT Sensor is connected to GPIO17
sensor = 11
pin = 17

#Soil Moisture sensor is connected to GPIO14 as a button
soil = Button(14)

flag = 1

pump.on()

class MySubscribeCallback(SubscribeCallback):
    global flag

    def status(self, pubnub, status):
        pass

    def presence(self, pubnub, presence):
        pass

    def message(self, pubnub, message):
        if message.message == 'ON':
        	flag = 1
        elif message.message == 'OFF':
			flag = 0
        elif message.message == 'WATER':
        	pump.off()
        	sleep(5)
        	pump.on()
 
 
pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('ch1').execute()

def publish_callback(result, status):
	pass

def get_status():
	if soil.is_held:
        print("wet")
        return False
	else:
        print("dry")
        return True


while True:
	if flag ==1:
		# Try to grab a sensor reading.  Use the read_retry method which will retry up
		# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
		humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
		DHT_Read = ('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
		print(DHT_Read)

		dictionary = {"eon": {"Temperature": temperature, "Humidity": humidity}}
		pubnub.publish().channel('ch2').message([DHT_Read])
		pubnub.publish().channel("eon-chart").message(dictionary)

		wet = get_status()
		
		if wet == True:
		    print("turning on")
		    pump.off()
		    sleep(5)
		    print("pump turning off")
		    pump.on()
		    sleep(1)
		else:
		    pump.on()

		sleep(1)
	elif flag == 0:
		pump.on()
		sleep(3)
