from st2actions.runners.pythonrunner import Action

from lib import Secure_Shell
from lib import Telnet
from lib import ztp_utils

import json

class SendConfigurationCommandAction(Action):
    def __init__(self, config):
        super(SendConfigurationCommandAction, self).__init__(config)
        self._username = self.config['username']
        self._password = self.config['password']
        self._enable_username = self.config['enable_username']
        self._enable_password = self.config['enable_password']

    def run(self, via, device, command, username='', password='', enable_username='', enable_password=''):
	if not username:
		username = self._username
	if not password:
		password = self._password
	if not enable_username:
		enable_username = self._enable_username
	if not enable_password:
		enable_password = self._enable_password

	devices = device.split(',')
        device_output=[]
        has_failures=False
        for d in devices:
                if via == 'telnet':
                        session = Telnet.Telnet(d, username, password, enable_username, enable_password)
                if via == 'ssh':
                        session = Secure_Shell.Secure_Shell(d, username, password, enable_username, enable_password)

                (success,output) = ztp_utils.send_commands_to_session(session,command,conf_mode=True)
                if success:
                        device_output.append({"device":d,"output":output})
                else:
                        device_output.append({"device":d,"output":"Failed to connect!"})
                        has_failures=True


        if len(devices)==1 and has_failures:
                return (False,"Failed to connect!")

        return (True, device_output)

