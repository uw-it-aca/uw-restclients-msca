# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_msca.delegate import get_delegates, get_all_delegates
from uw_msca.util import fdao_msca_override
import mock


@fdao_msca_override
class GetDelegatesTest(TestCase):
    def test_get_delegates(self):
        delegates = get_delegates('javerage')
        self.assertEqual(len(delegates), 2)

        delegates = get_delegates('bill')
        self.assertEqual(len(delegates), 1)

    @mock.patch('uw_msca.delegate.get_external_resource')
    def test_get_all_delegates(self, mock_method):
        delegates = get_all_delegates()
        mock_method.assert_called_with(
            "https://host/blob/MbxAll-Report-date.csv")

