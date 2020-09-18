from pysys.constants import *
from pysys.utils.filegrep import *
from pysys.utils.linecount import *
from apama.correlator import CorrelatorHelper
from os import path
import time

class GAPDemoStandaloneHelper:
	def __init__(self, parent, project):
		super(GAPDemoStandaloneHelper, self).__init__()
		self.parent = parent
		self.project = project

	def startApplication(self):
		correlator = CorrelatorHelper(self.parent, name='defaultCorrelator')
		correlator.start(logfile='correlator.log')
		receiver = correlator.receive(filename='receive.evt', logChannels=True)
		
		correlator.injectEPL(filenames=['Cumulocity_EventDefinitions.mon'],
			filedir=os.path.join(self.project.APAMA_MONITORS_DIR, 'cumulocity', '10.5'))
		correlator.injectEPL(filenames=['GAPDemo.mon'],
			filedir=self.project.MONITORS_DIR)
		
		self.parent.waitForSignal('receive.evt', expr="com.apama.cumulocity.FindManagedObject", condition="==1")
		self.correlator = correlator
		return correlator

	def getDeviceDetails(self):
		self.parent.log.info('Getting device details')
		reqId = getmatches(os.path.join(self.parent.output,'receive.evt'), regexpr="com.apama.cumulocity.FindManagedObject\(([0-9]+),")[0].group(1)
		phoneId = 1
		phoneName = "Phone1"		
		self.correlator.sendEventStrings(
			f'"cumulocity.finddevice.response",com.apama.cumulocity.FindManagedObjectResponse({reqId},"{phoneId}",com.apama.cumulocity.ManagedObject("{phoneId}","c8y_SensorPhone","{phoneName}",[],[],[],[],[],[],{{}},{{}}))',
			f'"cumulocity.finddevice.response",com.apama.cumulocity.FindManagedObjectResponseAck({reqId})')
		return (phoneId, phoneName)

	def sendAcceleration(self, deviceId, accelerationX, accelerationY, accelerationZ):
		self.parent.log.info(f'Posting "c8y_Acceleration" measurement to device "{deviceId}", X={accelerationX}, Y={accelerationY}, Z={accelerationZ}')
		self.correlator.sendEventStrings(
			f'"cumulocity.measurements",com.apama.cumulocity.Measurement("","c8y_Acceleration","{deviceId}",{time.time()},{{"c8y_Acceleration":{{"accelerationX":com.apama.cumulocity.MeasurementValue({accelerationX},"G",{{}}),"accelerationY":com.apama.cumulocity.MeasurementValue({accelerationY},"G",{{}}),"accelerationZ":com.apama.cumulocity.MeasurementValue({accelerationZ},"G",{{}})}}}},{{}})')

	def countActiveAlarms(self, type):
		self.parent.log.info(f'Getting active alarms of type "{type}"')
		return linecount(os.path.join(self.parent.output,'receive.evt'), regexpr=f'com.apama.cumulocity.Alarm."","{type}"')

	def waitForSubscription(self):
		self.parent.waitForSignal('receive.evt', expr='com.apama.cumulocity.SubscribeMeasurements', condition="==1")

	def waitForBaseline(self):
		self.parent.waitForSignal('correlator.log', expr='Received Z-acceleration measurement 1.23', condition="==1")
	
	def waitForMeasurements(self):
		self.correlator.flush()
		self.parent.waitForSignal('receive.evt', expr="com.apama.cumulocity.Alarm", condition=">=4")
