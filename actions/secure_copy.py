from st2actions.runners.pythonrunner import Action

from lib import Secure_Copy

class SecureCopyAction(Action):
    def __init__(self, config):
        super(SecureCopyAction, self).__init__(config)
        self._username = self.config['username']
        self._password = self.config['password']

    def run(self, hostname, source, destination, direction, username='', password=''):
	if not username:
		username = self._username
	if not password:
		password = self._password
	scp = Secure_Copy.Secure_Copy(hostname, username, password)
	scp.erase_existing_ssh_key_for_host()
	if direction == 'to':
		success = scp.send_file(source,destination)
	if direction == 'from':
		success = scp.get_file(source,destination)
	if success:
                return (True,"File Copied!")
	else:
		return (False,"Failed to Copy")


