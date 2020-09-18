from pysys.constants import *
from GAPDemoConnected import GAPDemoConnectedHelper
from requests import Session
from os import path
import json

class GAPDemoHostedHelper(GAPDemoConnectedHelper):
	def __init__(self, parent, project):
		super(GAPDemoHostedHelper, self).__init__(parent, project)

	def startApplication(self):
		with open(os.path.join(self.project.MONITORS_DIR, 'GAPDemo.mon'), 'r') as epl_file:
			response = json.loads(
				self.session.post(
					f'{self.c8y_url}service/cep/eplfiles',
						data=json.dumps({
							'name': 'GAPDemo',
							'description': '',
							'state': 'active',
							'contents': epl_file.read()
						})
				).text
			)
			self.eplId = response["id"]
			self.parent.addCleanupFunction(lambda: self.session.delete(f'{self.c8y_url}service/cep/eplfiles/{self.eplId}'))
		return self.eplId
