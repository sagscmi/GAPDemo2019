from pysys.constants import *
from apama.correlator import CorrelatorHelper
from requests import Session
from requests.auth import HTTPBasicAuth
from os import path
import json
import time

class GAPDemoConnectedHelper:
	def __init__(self, parent, project):
		super(GAPDemoConnectedHelper, self).__init__()
		self.parent = parent
		self.project = project

		self.c8y_url = PROJECT.C8Y_URL
		self.c8y_username = PROJECT.C8Y_USERNAME
		self.c8y_password = PROJECT.C8Y_PASSWORD
		
		self.session = Session()
		self.session.auth = HTTPBasicAuth(self.c8y_username, self.c8y_password)
		self.session.verify = True
		self.session.headers.update({
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		})

	def startApplication(self):
		correlator = CorrelatorHelper(self.parent, name='defaultCorrelator')
		correlator.start(logfile='correlator.log', config=[
			os.path.join(self.project.CONFIG_DIR, "CorrelatorConfig.yaml"),
			os.path.join(self.project.APAMA_CONNECTIVITY_DIR, 'standard-codecs.yaml'),
			os.path.join(self.project.APAMA_CONNECTIVITY_DIR, 'CumulocityConnectivity', '10.5', 'CumulocityIoTDynamic.yaml'),
			os.path.join(self.project.CONFIG_DIR, 'connectivity', 'CumulocityClient10.5+', 'CumulocityIoT.properties'),
			os.path.join(self.project.CONFIG_DIR, 'connectivity', 'CumulocityClient10.5+', 'CumulocityIoT.yaml'),
		])
		receiver = correlator.receive(filename='receive.evt', logChannels=True)
	
		correlator.initialize(path=self.project.DEPLOY_FILE, correlatorName="defaultCorrelator")
		
		self.parent.waitForSignal('receive.evt', expr="com.apama.cumulocity.FindManagedObject", condition="==1")
		self.correlator = correlator
		return correlator

	def getDeviceDetails(self):
		self.parent.log.info('Getting device details')
		devices = json.loads(self.session.get(f'{self.c8y_url}inventory/managedObjects?fragmentType=c8y_IsDevice&type=c8y_SensorPhone').text)
		phone = devices['managedObjects'][0]
		return (phone["id"], phone["name"])

	def sendAcceleration(self, deviceId, accelerationX, accelerationY, accelerationZ):
		self.parent.log.info(f'Posting "c8y_Acceleration" measurement to device "{deviceId}", X={accelerationX}, Y={accelerationY}, Z={accelerationZ}')
		request = {
			'c8y_Acceleration' : {
				'accelerationX' : {
					'value' : accelerationX,
					'unit' : 'G'
				},
				'accelerationY' : {
					'value' : accelerationY,
					'unit' : 'G'
				},
				'accelerationZ' : {
					'value' : accelerationZ,
					'unit' : 'G'
				}
			},
			'time' : time.strftime('%Y-%m-%dT%H:%M:%S%z'),
			'source' : {
				'id' : deviceId
			},
			'type' : 'c8y_Acceleration'
		}
		self.session.post(f'{self.c8y_url}measurement/measurements', json=request)

	def countActiveAlarms(self, type):
		self.parent.log.info(f'Getting active alarms of type "{type}"')
		response = json.loads(self.session.get(f'{self.c8y_url}alarm/alarms?type={type}&status=ACTIVE').text)
		count = 0
		for a in response["alarms"]:
			count += a["count"]
		return count

	def waitForSubscription(self):
		self.parent.wait(5.0)

	def waitForBaseline(self):
		self.parent.wait(5.0)
	
	def waitForMeasurements(self):
		self.parent.wait(5.0)
