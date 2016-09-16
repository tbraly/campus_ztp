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


class Telnet(Session.Session):

    def login(self):
        ''' Attempt to Login to Device '''
        # self.session_lf = '\r'
        COMMAND = "telnet %s" % (self.hostname)
        self.session = pexpect.spawn(COMMAND)
        self.session.logfile = open('/tmp/telnetlog', 'w')

        matches = ["Press <Enter> to accept and continue the login process....",
                   "User Access Verification",
                   "telnet@(.)+>",
                   "Unable to connect",
                   pexpect.TIMEOUT]

        while True:

            i = self.session.expect(matches)

            if i == 0:   # NEED TO ACK BANNER
                self.sendline('')

            if i == 1:   # NEED USER ACCESS VERIFICAITON
                while True:
                    j = self.session.expect(['Password:', 'Login Name:'])
                    if j == 0:
                        self.sendline(self.password)
                    if j == 1:
                        self.sendline(self.username)
                        m = self.session.expect(['Password:', pexpect.TIMEOUT], timeout=5)
                        if m == 0:
                            self.sendline(self.password)
                        if m == 1:
                            # Could this be a CER?
                            self.session_lf = '\r'
                            self.sendline('')
                            continue

                    k = self.session.expect(['successful', 'failure', pexpect.TIMEOUT])
                    if k == 0:
                        sys.stdout.write("Logged into %s successful\r\n" % self.hostname)
                        self.session.expect(['telnet@(.)+#', 'telnet@(.)+>'])
                        self.session_prompt = "%s" % self.session.after[0:-1]
                        if self.session.after[-1] == '>':
                            self.session_state = Session.Session.SESSION_AVAILABLE
                            return True
                        if self.session.after[-1] == '#':
                            self.session_state = Session.Session.PRIVILEDGE_MODE
                            return True

                    if k == 1:
                        sys.stderr.write("Invalid User/Pass for %s\r\n" % self.hostname)
                        return False
                    if k == 2:
                        # Could this be a CER?
                        self.session_lf = '\r'
                        self.sendline('')

            if i == 2:   # NO PASSWORDS
                sys.stdout.write("Logged into %s without any passwords\r\n" %
                                 self.hostname)
                self.sendline('')
                self.session_prompt = "%s" % self.session.after[0:-1]
                # Is this a CER?
                self.sendline('')
                j = self.session.expect(['%s>' % self.session_prompt, pexpect.TIMEOUT],
                                        timeout=3)
                if j == 1:  # TIMEOUT
                    self.session_lf = '\r'
                    self.sendline('')
                self.session_state = Session.Session.SESSION_AVAILABLE
                return True

            if i == 3:   # UNABLE TO CONNECT
                sys.stderr.write("Could not connect to %s\r\n" % self.hostname)
                return False

            if i == 4:   # TIMEOUT
                # Could this be a CER?
                if not self.session_lf:
                    self.session_lf = '\r'
                    self.sendline('')
                else:
                    sys.stderr.write("Timed out trying to connect to %s\r\n" %
                                     self.hostname)
                    return False
