"""
Copyright 2016 Brocade Communications Systems, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from jinja2 import Template, Environment, StrictUndefined, UndefinedError, meta


class Template_Parser(object):

    def __init__(self, configuration_template_file, variables={}):
        ''' Loads the configuration file '''
        self.profile = ""
        self.variables = variables
        try:
            with open(configuration_template_file, 'r') as f:
                self.profile = "".join(line for line in f)
        except:
            raise IOError("Template file '%s' not found!", configuration_template_file)

    def set_variables(self, variables):
        ''' Sets the variables '''
        self.variables = variables

    def get_required_variables(self):
        ''' Returns a set of the required variables in the template '''
        return meta.find_undeclared_variables(Environment().parse(self.profile))

    def get_parsed_lines(self):
        ''' Returns a set of lines with all variables filed in '''
        try:
            return Template(self.profile, undefined=StrictUndefined).render(self.variables)
        except UndefinedError as e:
            raise Exception(e)
