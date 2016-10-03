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
from lib import actions
from lib import ztp_utils


class GetFlashAction(actions.SessionAction):
    def __init__(self, config):
        super(GetFlashAction, self).__init__(config)

    def run(self, via, device, username='', password='', enable_username='', enable_password=''):
        ztp_utils.replace_default_userpass(self, username, password,
                                           enable_username, enable_password)
        session = ztp_utils.start_session(device, self._username, self._password,
                                          self._enable_username, self._enable_password, via)

        command = 'show version'
        (success, results) = ztp_utils.send_commands_to_session(session, command, conf_mode=False)

        if success:
            # Built JSON Record from parsed results
            result = {}

            unit_and_version = re.compile('(^\s+UNIT )(\d+)(:.+)(labeled as )(.+)')
            boot = re.compile('(^\s+.+Boot-Monitor.+ Version:)([\d\w\.]+)')
            hardware = re.compile('(^\s+HW: )(Stackable )?([\w\d\-]+)')

            for line in results[0]['output']:
                match = unit_and_version.match(line)
                if match:
	            if 'firmware' not in results:
                        result['firmware']=[]
                    unit = match.group(2)
                    version = match.group(5)
                    result['firmware'].append({'unit': int(unit), 'version': version.upper()})
                match = hardware.match(line)
                if match:
                    print("matched hardware")
                    hardware_type = match.group(3)
                    result.update({'hardware': hardware_type.upper()})
                match = boot.match(line)
                if match:
                    boot_version = match.group(2)
                    result.update({'boot': boot_version.upper()})

            return (True, json.dumps(result))

        return (False, "Failed")
