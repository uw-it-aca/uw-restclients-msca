# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_msca.access_rights import get_access_rights
from uw_msca.util import fdao_msca_override


@fdao_msca_override
class AccessRightsTest(TestCase):
    def test_get_access_rights(self):
        access_rights = get_access_rights()
        self.assertEqual(len(access_rights), 4)
