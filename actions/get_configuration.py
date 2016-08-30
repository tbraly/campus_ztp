from st2actions.runners.pythonrunner import Action

from lib import Template_Parser
from lib import Excel_Reader

import sys,json

class GetConfigurationAction(Action):
    def __init__(self, config):
        super(GetConfigurationAction, self).__init__(config)
        self._template_dir = self.config['template_dir']
        self._excel_file = self.config['excel_file']

    def run(self, name, additional_variables='{}'):
	excel = Excel_Reader.Excel_Reader(self._excel_file)
        template_file_name = excel.get_template_name_for_key(name)
        variables = excel.get_variables_for_key(name)

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

                return (True,parse.get_parsed_lines())
	else:
		return (False,"Does not work")


