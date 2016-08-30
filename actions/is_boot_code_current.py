from st2actions.runners.pythonrunner import Action

import json
from lib import ztp_utils

class IsBootCodeCurrentAction(Action):
    def __init__(self, config):
        super(IsBootCodeCurrentAction, self).__init__(config)
        self._boot_image = self.config['boot_image']

    def run(self, images, keep_better):

        data = json.loads(images)

        # Strip off everything but numbers and patch
        boot = data["1"]["boot"].split('T')[0]

        # Strip off everything but numbers and patch
        new_boot = self._boot_image.split('.')[0]
        new_boot = "%s.%s.%s" % (new_boot[3:5],new_boot[5:6],new_boot[6:])

        if boot == new_boot:
                return (True,"Existing code is the same")

        if keep_better=='yes' and ztp_utils.compare_versions(boot, new_boot):
                return (True,"Existing code is better")

        return (False,"Existing code needs upgrading")
