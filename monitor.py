from time import sleep

class Monitor:

    def __init__(self):
    	self.__sensor = -1
    	'''
    	self.temperature_sensor = -1
    	self.humidity_sensor = -1
    	self.co2_sensor = -1
    	self.heater = -1
    	self.cooler = -1
    	self.irrigator = -1
    	self.co2_injector = -1
    	'''

    def showInfo(self):
    	while(1):
	    	print('Sensor: ', self.__sensor)
	    	sleep(0.5)



    def setSensor(sensor):
    	self.__sensor = sensor

