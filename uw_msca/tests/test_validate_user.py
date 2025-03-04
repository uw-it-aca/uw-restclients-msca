# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_msca.validate_user import validate_user
from uw_msca.util import fdao_msca_override


@fdao_msca_override
class ValidateUserTest(TestCase):
    def test_valid_user(self):
        validated = validate_user('javerage')
        self.assertTrue(validated.valid)

    def test_invalid_user(self):
        validated = validate_user('bill')
        self.assertFalse(validated.valid)
