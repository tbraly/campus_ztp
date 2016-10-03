import sys
import logging
import pexpect

class Session(object):

    NO_SESSION = 1
    SESSION_AVAILABLE = 2
    PRIVILEDGE_MODE = 3
    CONFIGURATION_MODE = 4

    def __init__(self, hostname, username='', password='', enable_username='', enable_password=''):
        ''' Sets up configuration to be transfered '''
        self.hostname = hostname
        self.username = username
        self.password = password
        self.enable_username = enable_username
        self.enable_password = enable_password
        self.session = None
        self.session_state = Session.NO_SESSION
        self.session_lf = ''
        self.session_prompt = ''

    def login(self):
        ''' Abstract Function to Login to Device - Must override '''

    def sendline(self, line):
        ''' Wrapper function to add LF or not '''
        self.session.sendline('%s%s' % (line, self.session_lf))

    def enter_enable_mode(self):
        ''' enters enable mode '''
        if self.session_state == Session.SESSION_AVAILABLE:
            prompt = self.session_prompt
            self.sendline('enable')
            c = self.session.expect(['assword:', 'Name:', '%s#' % prompt, pexpect.TIMEOUT])
            if c == 0:
                # is just asking for enable password
                self.sendline(self.enable_password)
            if c == 1:
                # is asking for username and password
                self.sendline(self.enable_username)
                self.session.expect('assword:')
                self.sendline(self.enable_password)
            if c == 2:
                # there is no enable password
                self.session_state = Session.PRIVILEDGE_MODE
                return True
            if c == 3:
                sys.stderr.write("Timeout trying to enter enable mode\r\n")
                return False

            # double check we are in enable mode
            i = self.session.expect(['assword:', 'Name:', '%s>' % prompt, '%s#' % prompt])
            if i < 3:
                # incorrect credentials
                # TODO: Terminate Login
                sys.stderr.write("Invalid enable username/password!\r\n")
                return False

            self.session_state = Session.PRIVILEDGE_MODE
            return True
        if self.session_state == Session.PRIVILEDGE_MODE:
            return True
        raise Exception("Trying to enter enable mode while State is not "
                        "Available or already in priviledge mode")
        return False

    def enter_configuration_mode(self):
        ''' enters configuration mode '''
        if self.session_state == Session.PRIVILEDGE_MODE:
            prompt = "\(config\)#"
            sys.stdout.write("Entering Configuration mode on %s\r\n" % self.hostname)
            self.sendline('configure terminal')
            i = self.session.expect([prompt, pexpect.TIMEOUT], timeout=5)
            if i == 0:
                self.session_state = Session.CONFIGURATION_MODE
                return True
            sys.stderr.write("Failed to enter configuration mode")
            return False
        else:
            raise Exception("Attempted to enter configuration mode when device "
                            "was not in priviledge mode on '%s'" % self.hostname)

    def exit_configuration_mode(self):
        ''' exits configuration mode '''
        if self.session_state == Session.CONFIGURATION_MODE:
            sys.stdout.write("Exiting Configuration mode on %s\r\n" % self.hostname)
            self.sendline('end')
            self.session.expect('#')
            self.sendline('')
            self.session.expect('#')
            sys.stdout.write("Exiting Configuration mode successful\r\n")
            self.session_state = Session.PRIVILEDGE_MODE
        else:
            raise Exception("Attempted to exit configuration mode when device "
                            "was not in configuration mode on '%s'" % self.hostname)

    def create_crypto_keys(self, keytype='rsa', modulus=2048):
        '''generates ssh keys. keytype can be either rsa or dsa, modules can be 1024 or 2048'''
        assert (modulus == 1024 or modulus == 2048)
        assert (keytype == 'dsa' or keytype == 'rsa')
        if self.session_state == Session.CONFIGURATION_MODE:
            sys.stdout.write("Configuring crypto keys on %s\r\n" % self.hostname)
            self.sendline('crypto key generate %s modulus %d' % (keytype, modulus))
            i = self.session.expect(['zeroize it', 'created', pexpect.TIMEOUT], timeout=120)
            if i == 0:
                self.sendline('crypto key zeroize rsa')
                self.session.expect('deleted')
                self.sendline('crypto key generate %s modulus %d' % (keytype, modulus))
                j = self.session.expect(['created', pexpect.TIMEOUT], timeout=120)
                if j == 0:
                    self.sendline('')
                    return True
                sys.stderr.write("Timed out creating keys\r\n")

            if i == 1:
                self.sendline('')
                return True
            sys.stderr.write("Timed out creating keys\r\n")
            return False
        else:
            raise Exception("Attempted to configuration crypto keys when device "
                            "was not in configuration mode on '%s'" % self.hostname)

    def page_on(self):
        if self.session_state == Session.PRIVILEDGE_MODE:
            prompt = "%s#" % self.session_prompt
            self.sendline('page')
            self.session.expect(prompt)

    def page_skip(self):
        if self.session_state == Session.PRIVILEDGE_MODE:
            prompt = "%s#" % self.session_prompt
            self.sendline('skip')
            self.session.expect(prompt)

    def send_line(self, line):
        ''' Set an arbitrary cli command - output is sent to stdout'''
        prompt = "%s#" % self.session_prompt

        if self.session_state == Session.CONFIGURATION_MODE:
            prompt = r'%s\((.).+\)#' % self.session_prompt

        self.sendline(line)

        i = 0

        # Record any output from the command
        output = []
        while self.session.expect(['\r\n', prompt]) == 0:
            # skip first line, as it's just a repeat of the command
            if i > 0:
                output.append(self.session.before)
            i = i + 1

        return output

    def set_hostname(self, hostname):
        ''' Set Hostname for testing '''
        sys.stdout.write("Setting hostname on %s\r\n" % self.hostname)
        if self.session_state == Session.CONFIGURATION_MODE:
            self.sendline("hostname %s" % hostname)
            self.session.expect('#')
            return True
        else:
            raise Exception("Attempted to configuration hostname while device "
                            "was not in configuration mode on '%s'" % self.hostname)

    def upgrade_code_by_tftp(self, tftp_server, filename, towhere):
        ''' Upgrades code to a location specified by 'towhere' '''
        assert(towhere == 'primary' or towhere == 'secondary' or towhere == 'bootrom')
        sys.stdout.write("Upgrading %s on %s\r\n" % (towhere, self.hostname))
        if self.session_state == Session.PRIVILEDGE_MODE:
            self.session.sendline('copy tftp flash %s %s %s' % (tftp_server, filename, towhere))
            self.session.sendline('\r\n')
            i = self.session.expect(['Done.', 'Error', 'please wait', pexpect.TIMEOUT],
                                    timeout=300)
            if i == 1:
                sys.stderr.write("TFTP error occurred trying to update %s code on %s\r\n" %
                                 (towhere, self.hostname))
                return False
            if i == 2:
                sys.stderr.write("Flash is busy during %s code upgrade on %s\r\n" %
                                 (towhere, self.hostname))
                return False
            if i == 3:
                sys.stderr.write("Timeout trying to update %s code on %s\r\n" %
                                 (towhere, self.hostname))
                return False

            sys.stdout.write("Upgrade of %s code successful on %s\r\n" % (towhere, self.hostname))
            return True
        raise Exception("Attempted to upgrade %s code while device was "
                        "not in priviledge mode on '%s'" % (towhere, self.hostname))
        return False

    def upgrade_bootcode_by_tftp(self, tftp_server, filename):
        ''' Upgrades boot code '''
        return self.upgrade_code_by_tftp(tftp_server, filename, 'bootrom')

    def reload(self, writemem=True):
        ''' reload device '''
        logging.debug("Reloading '%s'" % self.hostname)
        if self.session_state == Session.PRIVILEDGE_MODE:
            if writemem:
                self.session.sendline('write memory')
                self.session.expect('#')
            self.session.sendline('reload')
            i = self.session.expect(['\):',pexpect.TIMEOUT],timeout=2)
            if i == 1:   # FCX FIX
                self.session.send('\r\n') 
                self.session.expect('\):',timeout=2)
            self.session.send('y')
            i = self.session.expect(['\):', pexpect.EOF],timeout=2)
            if i == 0:
		self.session.sendline('y')
		self.session.sendline('')
		self.session.close()
            self.session_state = Session.NO_SESSION
        else:
            logging.warning("Attempted to logout when device was not priviledge "
                            "mode on '%s'" % self.hostname)

    def logout(self):
        ''' logout of device '''
        self.sendline('exit')
        self.sendline('exit')
        self.session.close()
        self.session_state = Session.NO_SESSION
        return

        # Or is this better?
        if self.session_state == Session.PRIVILEDGE_MODE:
            self.sendline('logout')
            self.session.expect(pexpect.EOF)

            self.session_state = Session.NO_SESSION
        else:
            logging.warning("Attempted to logout when device was not priviledge "
                            "mode on '%s'" % self.hostname)
