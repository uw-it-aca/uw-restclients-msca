# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from urllib3 import PoolManager
from urllib3.util.retry import Retry
from os.path import abspath, dirname
from restclients_core.dao import DAO


class MSCA_DAO(DAO):
    def service_name(self):
        return 'msca'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _custom_headers(self, method, url, headers, body):
        return {"Ocp-Apim-Subscription-Key": "{}".format(
            self.get_service_setting("SUBSCRIPTION_KEY", ""))}

    def getURL(self, url, headers={}, body=None):
        return self._load_resource("GET", url, headers, body)

    def get_external_resource(self, url, body=None):
        http = PoolManager(
            retries=Retry(total=1, connect=0, read=0, redirect=1))
        return http.request('GET', url, body=body)
