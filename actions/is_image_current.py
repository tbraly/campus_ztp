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

import json
from st2actions.runners.pythonrunner import Action
from lib import ztp_utils


class IsImageCurrentAction(Action):
    def __init__(self, config):
        super(IsImageCurrentAction, self).__init__(config)
        self._images = self.config['software_images']

    def run(self, images, keep_better):

        # {"hardware": "ICX7750-48F", "firmware": [{"version": "SWS08040A", "unit": 1}], "boot": "10.1.06T205"}
        data = json.loads(images)

        hardware = data['hardware'][0:7]
        self._image=self._images['Brocade'][hardware]

        # TODO: Check if existing image is router vs switch in decision to replace!

        # Strip off everything but numbers and patch
        image = data["firmware"][0]['version']
        image = "%s.%s.%s" % (image[3:5], image[5:6], image[6:])

        # Strip off everything but numbers and patch
        new_image = self._image.split('.')[0]
        new_image = "%s.%s.%s" % (new_image[3:5], new_image[5:6], new_image[6:])

        if image.upper() == new_image.upper():
            return (True, "Existing code is the same")

        if keep_better == 'yes' and ztp_utils.compare_versions(image.upper(),new_image.upper()):
            return (True, "Existing code is better")

        return (False, self._image)
