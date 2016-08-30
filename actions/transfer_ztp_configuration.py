from st2actions.runners.pythonrunner import Action

from lib import Secure_Shell
from lib import Secure_Copy
from lib import Telnet
from lib import Template_Parser
from lib import Excel_Reader

import sys,os,uuid,json

class TransferZTPConfigurationAction(Action):
    def __init__(self, config):
        super(TransferZTPConfigurationAction, self).__init__(config)
        self._username = self.config['username']
        self._password = self.config['password']
        self._enable_username = self.config['enable_username']
        self._enable_password = self.config['enable_password']
        self._template_dir = self.config['template_dir']
        self._excel_file = self.config['excel_file']
        self._temp_dir = self.config['temp_dir']
        self._filename = "%s/%s" % (self._temp_dir,uuid.uuid4())

    def run(self, via, device, excel_key, additional_variables='{}', username='', password='', enable_username='', enable_password=''):
	if not username:
		username = self._username
	if not password:
		password = self._password
	if not enable_username:
		enable_username = self._enable_username
	if not enable_password:
		enable_password = self._enable_password

	if via == 'telnet':
		session = Telnet.Telnet(device, username, password, enable_username, enable_password)
	if via == 'ssh':
		session = Secure_Shell.Secure_Shell(device, username, password, enable_username, enable_password)
	if session.login():
		if session.enter_enable_mode():
			# Now create configuration and save out to a unique file
        		excel = Excel_Reader.Excel_Reader(self._excel_file)
        		template_file_name = excel.get_template_name_for_key(excel_key)
        		variables = excel.get_variables_for_key(excel_key)

                        # add additional variables
                        try:
                                additional_variables = json.loads(additional_variables)
                        except ValueError as e:
                                sys.stderr.write("additional_variables is not in JSON format!\r\n")
                                return (False,"Broken")

                        # check to see if there is any overlap with excel and warn!
                        for var in additional_variables:
                                if var in variables:
                                        sys.stdout.write("Warning: additional variable '%s' is overriding excel variable\r\n" % var)

                        # update the dictionary file with the new variables
                        variables.update(additional_variables)

        		if (template_file_name != ""):
                		parse = Template_Parser.Template_Parser("%s/%s" % (self._template_dir,template_file_name))
                		parse.set_variables(variables)

				# Check to make sure all variables have answers
				parse_success = True
				for v in parse.get_required_variables():
					if not v in variables:
						sys.stderr.write("Could not find variable '%s' in excel for template '%s'\r\n" % (v,template_file_name))
						parse_success = False
				if not parse_success:
					return (False,"Broken")
						

				try:
                			file = open(self._filename,'w')
                			file.write(parse.get_parsed_lines())
                			file.close()
				except IOError:
					sys.stderr.write("Could not write out configuration to temp file on server\r\n")
					session.logout()
					return (False,"Broken")

				scp = Secure_Copy.Secure_Copy(device, username, password)
		
				# TODO: This should be done when generate_keys is done
				scp.erase_existing_ssh_key_for_host()

				if scp.send_file(self._filename,'StartConfig'):
					session.reload(writemem=False)
                        		os.remove(self._filename)
					return (True,"Worked")
					
                        	os.remove(self._filename)
			else:
				# Something went wrong with creating configuration
				sys.stderr.write("No template defined in excel spreadsheet\r\n") 
				session.logout()

	return (False,"Broken")
