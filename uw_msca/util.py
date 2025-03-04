# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.util.decorators import use_mock
from uw_msca.dao import MSCA_DAO


fdao_msca_override = use_mock(MSCA_DAO())
