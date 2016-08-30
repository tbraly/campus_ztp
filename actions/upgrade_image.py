from st2actions.runners.pythonrunner import Action

from lib import Secure_Shell
from lib import Telnet

import time

class UpgradeImageAction(Action):
    def __init__(self, config):
        super(UpgradeImageAction, self).__init__(config)
        self._username = self.config['username']
        self._password = self.config['password']
        self._enable_username = self.config['enable_username']
        self._enable_password = self.config['enable_password']
        self._tftpserver = self.config['tftp_server']
        self._filename = self.config['software_image']

    def run(self, via, device, flash, tftp_server='', filename='', username='', password='', enable_username='', enable_password=''):
	if not username:
		username = self._username
	if not password:
		password = self._password
	if not enable_username:
		enable_username = self._enable_username
	if not enable_password:
		enable_password = self._enable_password
	if not tftp_server:
		tftp_server = self._tftpserver
	if not filename:
		filename = self._filename

	success=False
	if via == 'telnet':
		session = Telnet.Telnet(device, username, password, enable_username, enable_password)
	if via == 'ssh':
		session = Secure_Shell.Secure_Shell(device, username, password, enable_username, enable_password)
	if session.login():
		if session.enter_enable_mode():
			if session.upgrade_code_by_tftp(tftp_server,filename,flash):
				session.logout()
				success=True

	if success:
                return (True,"Worked")
	else:
		return (False,"Failed")


