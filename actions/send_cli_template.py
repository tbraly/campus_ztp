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

import sys
import json
from lib import actions, ztp_utils


class SendCLITemplateAction(actions.SessionAction):
    def __init__(self, config):
        super(SendCLITemplateAction, self).__init__(config)
        self._template_dir = self.config['template_dir']

    def run(self, via, device, template, template_dir='', variables='{}',
            conf_mode=False, username='', password='', enable_username='', enable_password=''):
        ztp_utils.replace_default_userpass(self, username, password,
                                           enable_username, enable_password)

        if template_dir:
            self._template_dir = template_dir

        if variables:
            try:
                variables = json.loads(variables)
            except ValueError:
                sys.stderr.write("variables is not in JSON format!\r\n")
                return (False, "Failed")

        # Process Template
        (success, command) = ztp_utils.process_template(template, self._template_dir, variables)
        if not success:
            return (False, 'Failed')

        devices = device.split(',')
        device_output = []
        has_failures = False
        for d in devices:
            session = ztp_utils.start_session(d, self._username, self._password,
                                              self._enable_username, self._enable_password, via)
            (success, output) = ztp_utils.send_commands_to_session(session, command, conf_mode)
            if success:
                device_output.append({"device": d, "output": output})
            else:
                device_output.append({"device": d, "output": "Failed"})
                has_failures = True

        if len(devices) == 1 and has_failures:
            return (False, "Failed")

        return (True, device_output)
