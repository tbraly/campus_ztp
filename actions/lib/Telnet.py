import Session
import pexpect
import sys

class Telnet(Session.Session):

	def login(self):
		''' Attempt to Login to Device '''
		#self.session_lf = '\r'
		COMMAND="telnet %s" % (self.hostname)
		try:
			self.session = pexpect.spawn(COMMAND)
			self.session.logfile = open('telnetlog','w')

			i = self.session.expect([pexpect.TIMEOUT, 'assword:','Name:','>'],timeout=500)
			if i==0 :
				# Connection Timed out
				sys.stderr.write("Connection to '%s' timed out." % self.hostname)
				return False
			if i==1 :
				# is just asking for telnet password
				self.sendline(self.password)
			if i==2 :
				# is asking for username and password
				self.sendline(self.username)
				self.session.expect('assword:')
				self.sendline(self.password)
			if i==3 :
				# no username or password required
				self.session_state = Session.Session.SESSION_AVAILABLE
				# Lets see if this is a CER!!!!
				ok = self.CER_check_and_fix()
				self.session_prompt = "%s" % self.session.before.split()[-1]
				return ok

			# Should be logged in at this point
			i = self.session.expect(['assword:','Name:','>','#',pexpect.TIMEOUT],timeout=3)
			if i<2 :
				# incorrect credentials
				# TODO: Terminate Login
				sys.stderr.write("Invalid login username/password for '%s'" % self.hostname)
				return False
			if i==2 :
				self.session_state = Session.Session.SESSION_AVAILABLE
			if i==3 :
				self.session_state = Session.Session.PRIVILEDGE_MODE
			if i==4 :
				sys.stderr.write("Login process timed out")
				return False

			ok = self.CER_check_and_fix()
			self.session_prompt = "%s" % self.session.before.split()[-1]
			return ok
			
		except:
			# Telnet timeout
			sys.stderr.write("Unable to telnet to '%s'" % self.hostname)
		
			# Command timeout
			return False
	
	def CER_check_and_fix(self):
		''' Check to see if we need to do \r along with \n on commands! '''
		self.sendline('')
		i = self.session.expect(['>','#',pexpect.TIMEOUT],timeout=2)
		if i==2:
			self.session_lf = '\r'
			self.sendline('')
			i = self.session.expect(['>','#',pexpect.TIMEOUT],timeout=2)
			if i==2:
				sys.stderr.write("CER Check Failed")
				return False
		return True	
