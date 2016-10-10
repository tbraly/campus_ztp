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

import json
import re
import sys
import Secure_Shell
import Telnet
import Excel_Reader
import Template_Parser

def process_template(template_file_name, template_dir, variables):
    ''' Loads JINJA2 template and process it with supplied variables '''
    if template_file_name != "":
        try:
            parse = Template_Parser.Template_Parser("%s/%s" % (template_dir, template_file_name))
        except IOError:
            sys.stderr.write("Could not load template file '%s/%s'" %
                             (template_dir, template_file_name))
            return (False, "Failed")
        parse.set_variables(variables)

        # Check to make sure all variables have answers
        parse_success = True
        for v in parse.get_required_variables():
            if (not variables) or (variables and v not in variables):
                sys.stderr.write("Could not find variable '%s' for template '%s'\r\n" %
                                 (v, template_file_name))
                parse_success = False
        if not parse_success:
            return (False, "Failed")

        return (True, parse.get_parsed_lines())
    else:
        return (False, "Failed")


def create_configuration(device, excel_file, template_dir, additional_variables):
    excel = Excel_Reader.Excel_Reader(excel_file)
    template_file_name = excel.get_template_name_for_key(device)
    variables = excel.get_variables_for_key(device)

    # add additional variables
    try:
        additional_variables = json.loads(additional_variables)
    except ValueError:
        sys.stderr.write("additional_variables is not in JSON format!\r\n")
        return (False, "Failed")

    # check to see if there is any overlap with excel and warn!
    for var in additional_variables:
        if var in variables:
            sys.stdout.write("Warning: additional variable '%s' overrides excel variable\r\n" %
                             var)

    # update the dictionary file with the new variables
    variables.update(additional_variables)

    return process_template(template_file_name, template_dir, variables)

def get_variables_for_key(excel_key, excel_file, variables):
    excel = Excel_Reader.Excel_Reader(excel_file)
    vfk = excel.get_variables_for_key(excel_key)
    if variables == '[]':  # default
        return vfk
    try:
        variables = json.loads(variables)
    except:
        sys.stderr.write("Filter variable(s) not in json array format")
    filtered = {}
    for v in variables:
        if v in vfk:
            filtered[v]=vfk[v]
    return filtered

def compare_versions(existing_version, new_version):
    ''' Input: ##.##.##aa  Output: True if the existing code is less the new.'''

    regex = re.compile('([0-9]+)\.([0-9]+)\.([0-9]+)([a-zA-Z]*)')

    existing_version_match = regex.match(existing_version)
    new_version_match = regex.match(new_version)

    for i in range(1, 5):
        if i < 4 and int(existing_version_match.group(i)) < int(new_version_match.group(i)):
            return False
        if i == 4 and existing_version_match.group(4) < new_version_match.group(4):
            return False

    return True


def send_commands_to_session(session, command, conf_mode=False):
    ''' sends a series of cli lines to a device (seperated by ';') '''
    output = []

    # if command list comes in seperated by newline, replace with ';'
    command = command.replace('\n', ';')

    # split command list into individual lines
    commands = command.split(';')

    if session.login():
        if session.enter_enable_mode():
            session.page_skip()
            if conf_mode:
                session.enter_configuration_mode()
            for line in commands:
                output.append({"output": session.send_line(line),"command": line})
            if conf_mode:
                session.exit_configuration_mode()
            session.page_on()

            return (True, output)

    return (False, {})

def replace_default_userpass(action, username, password, enable_username, enable_password):
    if username:
        action._username = username
    if password:
        action._password = password
    if enable_username:
        action._enable_username = enable_username
    if enable_password:
        action._enable_password = enable_password


def start_session(device, username, password, enable_username, enable_password, via):
    session = None
    if via == 'telnet':
        session = Telnet.Telnet(device, username, password,
                                enable_username, enable_password)
    if via == 'ssh':
        session = Secure_Shell.Secure_Shell(device, username, password,
                                            enable_username, enable_password)
    return session
