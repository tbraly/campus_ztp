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
import Session
import pexpect


class Secure_Shell(Session.Session):

    def login(self):
        ''' Attempt to Login to Device '''
        COMMAND = "ssh %s@%s" % (self.username, self.hostname)
        self.session = pexpect.spawn(COMMAND)
        self.session.logfile = open('/tmp/campus_ztp.sshlog', 'w')
        i = self.session.expect(['timed out', 'assword:', 'yes/no', 'failed', pexpect.TIMEOUT],
                                timeout=30)
        if i == 0:
            sys.stderr.write("SSH Connection to '%s' timed out" % self.hostname)
            return False
        if i == 1:
            self.session.sendline(self.password)
        if i == 2:
            self.session.sendline('yes')
            self.session.expect('assword:')
            self.session.sendline(self.password)
        if i == 3:
            sys.stderr.write("Known key failed to match device key!\r\n")
            return False
        if i == 4:
            sys.stderr.write("Failed to connect!\r\n")
            return False

        # Should be logged in at this point
        i = self.session.expect(['assword:', '>', '#', pexpect.TIMEOUT], timeout=15)
        if i == 0:
            # incorrect credentials
            # TODO: Terminate Login
            sys.stderr.write("Invalid login username/password for '%s'" % self.hostname)
            return False
        if i == 1:
            self.session_state = Session.Session.SESSION_AVAILABLE
        if i == 2:
            self.session_state = Session.Session.PRIVILEDGE_MODE
        if i == 3:
            sys.stderr.write("Failed to connect!\r\n")
            return False

        self.session_prompt = "%s" % self.session.before.split()[-1]
        return True
