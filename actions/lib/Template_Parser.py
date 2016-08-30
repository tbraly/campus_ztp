from jinja2 import Template,Environment,FileSystemLoader,StrictUndefined,UndefinedError,TemplateNotFound,meta

class Template_Parser(object):

        def __init__(self,configuration_template_file, variables = {}):
                ''' Loads the configuration file '''
                self.profile = ""
                self.variables = variables
                try:
                        with open(configuration_template_file,'r') as f:
                                self.profile = "".join(line for line in f)
                except:
                        raise Exception("Template file '%s' not found!", configuration_template_file)

        def set_variables(self,variables):
                ''' Sets the variables '''
                self.variables = variables

        def get_required_variables(self):
                ''' Returns a set of the required variables in the template '''
                return meta.find_undeclared_variables(Environment().parse(self.profile))

        def get_parsed_lines(self):
                ''' Returns a set of lines with all variables filed in '''
                try:
                        return Template(self.profile,undefined=StrictUndefined).render(self.variables)
                except UndefinedError as e:
                        raise Exception(e)

