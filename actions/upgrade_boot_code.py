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

from lib import actions, ztp_utils


class UpgradeBootCodeAction(actions.SessionAction):
    def __init__(self, config):
        super(UpgradeBootCodeAction, self).__init__(config)
        self._tftpserver = self.config['tftp_server']

    def run(self, via, device, tftp_server='', filename='', username='',
            password='', enable_username='', enable_password=''):
        ztp_utils.replace_default_userpass(self, username,
                                           password, enable_username, enable_password)

        if tftp_server:
            self._tftpserver = tftp_server
        if filename:
            self._filename = filename

        session = ztp_utils.start_session(device, self._username, self._password,
                                          self._enable_username, self._enable_password, via)

        if session.login():
            if session.enter_enable_mode():
                if session.upgrade_bootcode_by_tftp(self._tftpserver, self._filename):
                    session.logout()
                    return (True, "Success")

        return (False, "Failed")
