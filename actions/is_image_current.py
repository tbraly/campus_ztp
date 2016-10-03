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
import re
from st2actions.runners.pythonrunner import Action
from lib import ztp_utils


class IsImageCurrentAction(Action):
    def __init__(self, config):
        super(IsImageCurrentAction, self).__init__(config)
        self._images = self.config['software_images']

    def run(self, images, keep_better):

        # {"hardware": "ICX7750-48F", "firmware": [{"version": "SWS08040A", "unit": 1}], "boot": "10.1.06T205"}
        data = json.loads(images)

        hardware = data['hardware'].split('-')[0]
        self._image=self._images['Brocade'][hardware]

        # Strip off everything but numbers and patch
        image = data["firmware"][0]['version']
        match = re.compile('([a-zA-Z]+)([0-9]+[a-zA-Z]*)').match(image)
        imagetype = match.group(1)
        image = match.group(2)
        image = "%s.%s.%s" % (image[0:2], image[2:3], image[3:])

        # Strip off everything but numbers and patch
        new_image = self._image.split('.')[0]
        match = re.compile('([a-zA-Z]+)([0-9]+[a-zA-Z]*)').match(new_image)
        new_imagetype = match.group(1)
        new_image = match.group(2)
        new_image = "%s.%s.%s" % (new_image[0:2], new_image[2:3], new_image[3:])
        if image.upper() == new_image.upper() and imagetype.upper() == new_imagetype.upper():
            return (True, "Existing code is the same")

        if not imagetype.upper() == new_imagetype.upper():
            print('Note: Router vs switch mis-match')
            return (False,self._image)

        if keep_better == 'yes' and ztp_utils.compare_versions(image.upper(),new_image.upper()):
            return (True, "Existing code is better")

        return (False, self._image)
