import re
import Session

def compare_versions(existing_version, new_version):
        ''' Input: ##.##.##aa  Output: True if the existing code is less the new.'''

        regex = re.compile('([0-9]+)\.([0-9]+)\.([0-9]+)([a-z]*)')

        existing_version_match = regex.match(existing_version)
        new_version_match = regex.match(new_version)

        for i in range(1,5):
                if i<4 and int(existing_version_match.group(i))<int(new_version_match.group(i)):
                        return False
                if i==4 and existing_version_match.group(4)<new_version_match.group(4):
                        return False

        return True


def send_commands_to_session(session, command, conf_mode=False):
	''' sends a series of cli lines to a device (seperated by ';') '''
        output = []
        commands = command.split(';');

        if session.login():
                if session.enter_enable_mode():
                        session.page_skip()
                        if (conf_mode):
				session.enter_configuration_mode()
                        for line in commands:
                                output.append({"command": line, "output": session.send_line(line)})
			if (conf_mode):
                        	session.exit_configuration_mode()
                        session.page_on()

                        return (True,output)
	return (False,{})
