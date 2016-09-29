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

from st2actions.runners.pythonrunner import Action
from lib import ztp_utils


class GetExcelVariablesAction(Action):
    def __init__(self, config):
        super(GetExcelVariablesAction, self).__init__(config)
        self._excel_file = self.config['excel_file']

    def run(self, excel_key, variables=''):
        return ztp_utils.get_variables_for_key(excel_key, self._excel_file, variables)
