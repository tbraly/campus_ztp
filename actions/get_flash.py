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
		results = session.send_line('show flash')
		session.logout()
		success=True

	if success:
		# Built JSON Record from parsed results
		flash = {}
		unit = re.compile('^Stack unit [0-9]+')
		primary = re.compile('(.)+Pri(.)+Version(.)+')
		secondary = re.compile('(.)+Sec(.)+Version(.)+')
		boot = re.compile('(.)+Boot-Monitor(.)+Version(.)+')
		for line in results:
			match = unit.match(line)
			if match:
				unit_number = match.group().split()[-1]
				flash[unit_number]={}
			match = primary.match(line)
			if match:
				version = match.group().split(':')[-1].split()[0]
				flash[unit_number].update({'primary':version})
			match = secondary.match(line)
			if match:
				version = match.group().split(':')[-1].split()[0]
				flash[unit_number].update({'secondary':version})
			match = boot.match(line)
			if match:
				version = match.group().split(':')[-1].split()[0]
				flash[unit_number].update({'boot':version})

			
                return (True,json.dumps(flash))
	else:
		return (False,"Broken")


