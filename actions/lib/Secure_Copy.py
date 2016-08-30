import os,uuid
import pexpect
import subprocess

class Secure_Copy(object):

        def __init__(self, hostname, username = 'admin', password = 'admin'):
                ''' Sets up configuration to be transfered '''
                self.hostname = hostname
                self.username = username
                self.password = password

	def erase_existing_ssh_key_for_host(self):
		''' Erases the key stored on server (useful when IP's are re-used)'''
                command='ssh-keygen -f /root/.ssh/known_hosts -R %s 1>/dev/null 2>/dev/null' % (self.hostname)
                os.system(command)

        def run_scp(self,command):
                ''' Sends the file to the device '''
                success = False

                child = pexpect.spawn(command)
		child.logfile = open('securecopylog','w')
                i = child.expect(['yes/no','assword:','connection',pexpect.EOF])
                if i==0:
                        # GO AHEAD AND SAY YES TO A NEW KEY FOUND
                        child.sendline('YES')
                        child.expect('assword:')
                        child.sendline(self.password)
                if i==1:
                        child.sendline(self.password)
                if i==2:
			# Could not connect to device
			sys.stderr.write('Could not connect to device for secure copy\r\n')
                        success = False
		if i==3:
			# Key has changed on the device
			success = False
			return success

		# Check to make sure password was correct
		i = child.expect(['assword:',pexpect.EOF])
		if i==0:
			# Password supplied was incorrect
			sys.stderr.write('Username/Password is incorrect\r\n')
			success = False
		if i==1:
			# Assume it all worked
			success = True
			
		return success

	def send_file(self,sfile,dfile):
                command="scp -q -oPubKeyAuthentication=no %s %s@%s:%s" % (sfile,self.username,self.hostname,dfile)
		return self.run_scp(command)

	def get_file(self,sfile,dfile):
                command="scp -q -oPubKeyAuthentication=no %s@%s:%s %s" % (self.username,self.hostname,sfile,dfile)
		return self.run_scp(command)
