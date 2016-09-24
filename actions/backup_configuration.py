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
import time
from lib import actions, Secure_Copy, ztp_utils


class TransferZTPConfigurationAction(actions.SessionAction):
    def __init__(self, config):
        super(TransferZTPConfigurationAction, self).__init__(config)
        self._config_archive_dir = self.config['config_backup_dir']

    def run(self, device, username='', password=''):
        ztp_utils.replace_default_userpass(self, username, password, enable_username='', enable_password='')

	config_dir = '%s/%s' % (self._config_archive_dir,device)
        try:
            # Create directory for device if it doesn't exist
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
        except IOError:
            sys.stderr.write("Could not create directory for '%s'\r\n" % device)
            return (False, "Failed")

        scp = Secure_Copy.Secure_Copy(device, self._username, self._password)

        timestamp = int(time.time())
        filename = '%s/%s_%s.cfg' % (config_dir,device,timestamp)
        if scp.get_file('RunConfig', filename):
            return (True, "Success")

        return (False, "Failed")
