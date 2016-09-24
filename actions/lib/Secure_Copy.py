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

import os
import sys
import pexpect


class Secure_Copy(object):

    def __init__(self, hostname, username='admin', password='admin'):
        ''' Sets up configuration to be transfered '''
        self.hostname = hostname
        self.username = username
        self.password = password

    def erase_existing_ssh_key_for_host(self):
        ''' Erases the key stored on server (useful when IP's are re-used)'''
        command = 'ssh-keygen -f /root/.ssh/known_hosts -R %s 1>/dev/null 2>/dev/null' % \
                  (self.hostname)
        os.system(command)

    def run_scp(self, command):
        ''' Sends the file to the device '''
        success = False

        child = pexpect.spawn(command)
        child.logfile = open('/tmp/campus_ztp.securecopylog', 'w')
        i = child.expect(['yes/no', 'assword:', 'connection', pexpect.EOF])
        if i == 0:
            # GO AHEAD AND SAY YES TO A NEW KEY FOUND
            child.sendline('YES')
            child.expect('assword:')
            child.sendline(self.password)
        if i == 1:
            child.sendline(self.password)
        if i == 2:
            # Could not connect to device
            sys.stderr.write('Could not connect to device for secure copy\r\n')
            success = False
        if i == 3:
            # Key has changed on the device
            success = False
            return success

        # Check to make sure password was correct
        i = child.expect(['assword:', pexpect.EOF])
        if i == 0:
            # Password supplied was incorrect
            sys.stderr.write('Username/Password is incorrect\r\n')
            success = False
        if i == 1:
            # Assume it all worked
            success = True

        return success

    def send_file(self, sfile, dfile):
        command = "scp -q -o PubKeyAuthentication=no -o StrictHostKeyChecking=no %s %s@%s:%s" % \
                  (sfile, self.username, self.hostname, dfile)
        return self.run_scp(command)

    def get_file(self, sfile, dfile):
        command = "scp -q -o PubKeyAuthentication=no -o StrictHostKeyChecking=no %s@%s:%s %s" % \
                  (self.username, self.hostname, sfile, dfile)
        return self.run_scp(command)
