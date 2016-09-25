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

from st2client.client import Client
from st2client.models import KeyValuePair
from oslo_config import cfg
from keyczar.keys import AesKey
from st2common.util.crypto import symmetric_encrypt, symmetric_decrypt


class SessionAction(Action):
    def __init__(self, config):
        super(SessionAction, self).__init__(config)
        #self._username = self.config['username']
        #self._password = self.config['password']
        #self._enable_username = self.config['enable_username']
        #self._enable_password = self.config['enable_password']

        # Get Encryption Setup and Key
        is_encryption_enabled = cfg.CONF.keyvalue.enable_encryption
        if is_encryption_enabled:
             crypto_key_path = cfg.CONF.keyvalue.encryption_key_path
             with open(crypto_key_path) as key_file:
                 crypto_key = AesKey.Read(key_file.read())

        # Retrieve and decrypt values          
        client = Client(base_url='http://localhost')

        key = client.keys.get_by_name('campus_ztp.username')
        if key:
            self._username = key.value

        key = client.keys.get_by_name('campus_ztp.password')
        if key:
            self._password = symmetric_decrypt(crypto_key, key.value)

        key = client.keys.get_by_name('campus_ztp.enable_username')
        if key:
            self._enable_username = key.value

        key = client.keys.get_by_name('campus_ztp.enable_password')
        if key:
            self._enable_password = symmetric_decrypt(crypto_key, key.value)
