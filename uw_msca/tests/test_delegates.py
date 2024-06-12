# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_msca.delegate import get_delegates
from uw_msca.util import fdao_msca_override


@fdao_msca_override
class ValidateUserTest(TestCase):
    def test_get_delegates(self):
        delegates = get_delegates('javerage')
        self.assertEqual(len(delegates), 2)

        delegates = get_delegates('bill')
        self.assertEqual(len(delegates), 1)
