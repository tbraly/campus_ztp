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


class IsBootCodeCurrentAction(Action):
    def __init__(self, config):
        super(IsBootCodeCurrentAction, self).__init__(config)
        self._boot_images = self.config['boot_images']

    def run(self, images, keep_better):

	# {"hardware": "ICX7750-48F", "firmware": [{"version": "SWS08040A", "unit": 1}], "boot": "10.1.06T205"}
        data = json.loads(images)

        hardware = data['hardware'].split('-')[0]
        self._boot_image=self._boot_images['Brocade'][hardware]

        # Strip off everything but numbers and patch
        boot = data["boot"].split('T')[0]

        # Strip off everything but numbers and patch
        new_boot = self._boot_image.split('.')[0]
        new_boot = "%s.%s.%s" % (new_boot[3:5], new_boot[5:6], new_boot[6:])

        if boot == new_boot:
            return (True, "Existing code is the same")

        if keep_better == 'yes' and ztp_utils.compare_versions(boot, new_boot):
            return (True, "Existing code is better")

        #return (False, "Existing code needs upgrading")
        return (False, self._boot_image)
