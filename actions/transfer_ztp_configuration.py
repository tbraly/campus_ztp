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
import os
import uuid
from lib import actions, Secure_Copy, ztp_utils


class TransferZTPConfigurationAction(actions.SessionAction):
    def __init__(self, config):
        super(TransferZTPConfigurationAction, self).__init__(config)
        self._template_dir = self.config['template_dir']
        self._excel_file = self.config['excel_file']
        self._temp_dir = self.config['temp_dir']
        self._filename = "%s%s" % (self._temp_dir, uuid.uuid4())
        self._username = self.config['ztp_username']
        self._password = self.config['ztp_password']

    def run(self, via, device, excel_key, additional_variables='{}', username='', password='',
            enable_username='', enable_password=''):
        ztp_utils.replace_default_userpass(self, username, password,
                                           enable_username, enable_password)

        (success, config) = ztp_utils.create_configuration(excel_key, self._excel_file,
                                                           self._template_dir,
                                                           additional_variables)

        if success:
            session = ztp_utils.start_session(device, username, password,
                                              enable_username, enable_password, via)
            if session.login():
                if session.enter_enable_mode():
                    try:
                        cfg_file = open(self._filename, 'w')
                        cfg_file.write(config)
                        cfg_file.close()
                    except IOError:
                        sys.stderr.write("Could not write configuration to temp file\r\n")
                        session.logout()
                        return (False, "Failed")

                    scp = Secure_Copy.Secure_Copy(device, self._username, self._password)

                    # TODO: This should be done when generate_keys is done
                    scp.erase_existing_ssh_key_for_host()

                    if scp.send_file(self._filename, 'StartConfig'):
                        session.reload(writemem=False)
                        os.remove(self._filename)
                        return (True, "Success")

                    os.remove(self._filename)
                    
        sys.stderr.write("Could not generate configuration file from excel\r\n")
        return (False, "Failed")
