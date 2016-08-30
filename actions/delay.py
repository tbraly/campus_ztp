from st2actions.runners.pythonrunner import Action

import time

class DelayAction(Action):
    def __init__(self, config):
        super(DelayAction, self).__init__(config)

    def run(self, seconds):
	time.sleep(seconds)
        return True

