import sys
from Subfact_ina219 import INA219
import urllib2
from time import sleep
import Adafruit_DHT

def Power_consumption():
    read_current_sensor = INA219()
    current = read_current_sensor.getCurrent_mA()
    voltage = read_current_sensor.getBusVoltage_V()
    power = current*(0.001)*voltage
    return abs((int)(power))

#print "power : %.2f mW" % Power_consumption()


def Tempture():
    sensor = Adafruit_DHT.DHT22
    pin = 5
    humidity,temperature = Adafruit_DHT.read_retry(sensor,pin)
    if humidity is not None and temperature is not None:
        return (int)(temperature), (int)(humidity)

    return 0,0
    
#print "(Tempture, Humidty ): ",Tempture()


