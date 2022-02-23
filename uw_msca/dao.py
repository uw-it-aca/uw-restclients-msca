# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from os.path import abspath, dirname
from restclients_core.dao import DAO


class MSCA_DAO(DAO):
    def service_name(self):
        return 'msca'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _custom_headers(self, method, url, headers, body):
        return {"Ocp-Apim-Subscription-Key: {}".format(
            self.get_service_setting("SUBSCRIPTION_KEY", ""))}
