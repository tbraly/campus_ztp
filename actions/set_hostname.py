from st2actions.runners.pythonrunner import Action

from lib import Secure_Shell
from lib import Telnet

class SetHostnameAction(Action):
    def __init__(self, config):
        super(SetHostnameAction, self).__init__(config)
        self._username = self.config['username']
        self._password = self.config['password']
        self._enable_username = self.config['enable_username']
        self._enable_password = self.config['enable_password']

    def run(self, via, device, hostname, username='', password='', enable_username='', enable_password=''):
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
		if session.enter_enable_mode():
			if session.enter_configuration_mode():
				if session.set_hostname(hostname):
					session.exit_configuration_mode()
					session.send_line('show run | include hostname')
					session.logout()
					success=True
	if success:
                return (True,"Worked")
	else:
		return (False,"Broken")


