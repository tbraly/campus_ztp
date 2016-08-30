from st2actions.runners.pythonrunner import Action

from lib import Secure_Shell
from lib import Telnet

import re,json

class GetFlashAction(Action):
    def __init__(self, config):
        super(GetFlashAction, self).__init__(config)
        self._username = self.config['username']
        self._password = self.config['password']
        self._enable_username = self.config['enable_username']
        self._enable_password = self.config['enable_password']

    def run(self, via, device, username='', password='', enable_username='', enable_password=''):
	if not username:
		username = self._username
	if not password:
		password = self._password
	if not enable_username:
		enable_username = self._enable_username
	if not enable_password:
		enable_password = self._enable_password

	success=False
	if via == 'telnet':
		session = Telnet.Telnet(device, username, password, enable_username, enable_password)
	if via == 'ssh':
		session = Secure_Shell.Secure_Shell(device, username, password, enable_username, enable_password)
	if session.login():
		session.enter_enable_mode()
		results = session.send_line('show module | include ^U')
		session.logout()
		success=True

	if success:
		# Built JSON Record from parsed results
		modules = {}
		#unit = re.compile('^Stack unit [0-9]+')
		#primary = re.compile('(.)+Pri(.)+Version(.)+')
		#secondary = re.compile('(.)+Sec(.)+Version(.)+')
		#boot = re.compile('(.)+Boot-Monitor(.)+Version(.)+')
		last_unit=''
		for line in results:
			unit = line[0:7].split(':')[0][1:]
			module = line[0:7].split(':')[1][1:].rstrip()
			module_name = line[7:50].rstrip()
			ports = line[50:-1].split()[1]
			if unit!=last_unit:
				modules[unit]=[]
			modules[unit].append({"module":module,"name":module_name,"ports":ports})
			last_unit=unit
			
                return (True,json.dumps(modules))
	else:
		return (False,"Broken")


