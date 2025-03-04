# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

from uw_msca.models import (
    Quota,
)


class Test_Quota(TestCase):
    def test_to_str(self):
        assert Quota.to_str(100) == "100GB"
        assert Quota.to_str(1000) == "1000GB"
        assert Quota.to_str(9000) == "9000GB"

    def test_to_int(self):
        assert Quota.to_int("100GB") == 100
        assert Quota.to_int("1000GB") == 1000
        assert Quota.to_int("15000GB") == 15000

    def test_to_int_errors(self):
        with self.assertRaises(ValueError):
            Quota.to_int("100")
