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
        self._image = self.config['software_image']

    def run(self, images, keep_better):

        data = json.loads(images)

        # Strip off everything but numbers and patch
        image = data["1"]["primary"].split('T')[0]

        # Strip off everything but numbers and patch
        self._image = self._image.split('.')[0]
        new_image = "%s.%s.%s" % (self._image[3:5], self._image[5:6], self._image[6:])

        if image == new_image:
            return (True, "Existing code is the same")

        if keep_better == 'yes' and ztp_utils.compare_versions(image, new_image):
            return (True, "Existing code is better")

        return (False, "Existing code needs upgrading")
