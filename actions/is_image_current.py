from st2actions.runners.pythonrunner import Action

import json
from lib import ztp_utils

class IsImageCurrentAction(Action):
    def __init__(self, config):
        super(IsImageCurrentAction, self).__init__(config)
        self._image = self.config['software_image']

    def run(self, images, keep_better):

        data = json.loads(images)

        # Strip off everything but numbers and patch
        image = data["1"]["primary"].split('T')[0]

        # Strip off everything but numbers and patch
        self._image = self._image.split('.')[0]
        new_image = "%s.%s.%s" % (self._image[3:5],self._image[5:6],self._image[6:])

        if image == new_image:
                return (True,"Existing code is the same")

        if keep_better=='yes' and ztp_utils.compare_versions(image, new_image):
                return (True,"Existing code is better")

        return (False,"Existing code needs upgrading")
