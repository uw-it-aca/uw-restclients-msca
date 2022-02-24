# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_msca.access_types import get_access_types
from uw_msca.util import fdao_msca_override


@fdao_msca_override
class AccessTypesTest(TestCase):
    def test_access_types(self):
        access_types = get_access_types()
        self.assertEquals(len(access_types), 4)
