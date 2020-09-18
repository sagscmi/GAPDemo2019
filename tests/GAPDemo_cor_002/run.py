from pysys.constants import *
from apama.basetest import ApamaBaseTest
from apama.correlator import CorrelatorHelper
from GAPDemoConnected import GAPDemoConnectedHelper

class PySysTest(ApamaBaseTest):
	def __init__(self, descriptor, outsubdir, runner):
		super(PySysTest, self).__init__(descriptor, outsubdir, runner)
		self.helper = GAPDemoConnectedHelper(self, PROJECT)

	def execute(self):
		# Start application
		correlator = self.helper.startApplication()
		
		# Find a phone device
		(phoneId, phoneName) = self.helper.getDeviceDetails()
		self.log.info(f'Found c8y_SensorPhone device with name "{phoneName}" and id "{phoneId}"')

		# Wait for application to subscribe to measurements from the phone
		self.helper.waitForSubscription()

		# Set baseline acceleration
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, 1.23)
		
		# Wait for all events to be processed
		self.helper.waitForBaseline()

		# Get current active alarm counts
		flipUpBefore = self.helper.countActiveAlarms("FlipUp")
		self.log.info(f'Found {flipUpBefore} active "FlipUp" alarms before sending measurements')
		flipDownBefore = self.helper.countActiveAlarms("FlipDown")
		self.log.info(f'Found {flipDownBefore} active "FlipDown" alarms before sending measurements')
		
		# Send acceleration measurements
		self.log.info('Sending measurements...')
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, -0.9) # Up
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, 0.9)  # Down
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, 0.4)
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, 0.0)
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, -0.4)
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, -0.9) # Up
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, 0.8)
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, 0.9)
		self.helper.sendAcceleration(phoneId, 0.0, 0.0, 0.85) # Down
		
		# wait for all events to be processed
		self.helper.waitForMeasurements()

		# Get latest active alarm counts and calculate delta
		flipUpAfter = self.helper.countActiveAlarms("FlipUp")
		self.log.info(f'Found {flipUpAfter} active "FlipUp" alarms after sending measurements')
		flipDownAfter = self.helper.countActiveAlarms("FlipDown")
		self.log.info(f'Found {flipDownAfter} active "FlipDown" alarms after sending measurements')
		
		self.flipUpDelta = flipUpAfter - flipUpBefore
		self.flipDownDelta = flipDownAfter - flipDownBefore

	def validate(self):
		self.assertEval("self.flipUpDelta=={expected}", expected=2)
		self.assertEval("self.flipDownDelta=={expected}", expected=2)
