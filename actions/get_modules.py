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
from lib import actions, ztp_utils


class GetFlashAction(actions.SessionAction):
    def __init__(self, config):
        super(GetFlashAction, self).__init__(config)

    def run(self, via, device, username='', password='', enable_username='', enable_password=''):
        ztp_utils.replace_default_userpass(self, username, password,
                                           enable_username, enable_password)
        session = ztp_utils.start_session(device, self._username, self._password,
                                          self._enable_username, self._enable_password, via)

        command = 'show module | include ^U'
        (success, results) = ztp_utils.send_commands_to_session(session, command, conf_mode=False)

        if success:
            # Built JSON Record from parsed results
            modules = {}
            last_unit = ''
            for line in results[0]['output']:
                unit = line[0:7].split(':')[0][1:]
                module = line[0:7].split(':')[1][1:].rstrip()
                module_name = line[7:50].rstrip()
                ports = line[50:-1].split()[1]
                if unit != last_unit:
                    modules[unit] = []
                modules[unit].append({"module": module, "name": module_name, "ports": ports})
                last_unit = unit

            return (True, json.dumps(modules))

        return (False, "Failed")
