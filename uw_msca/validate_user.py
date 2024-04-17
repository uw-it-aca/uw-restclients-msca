# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UW MSCA outlook API
"""

import logging
import json
from uw_msca.models import ValidatedUser
from uw_msca import url_base, get_resource


logger = logging.getLogger(__name__)


def validate_user(name):
    """
    Returns whether or not given user has access to Outlook mailbox
    """
    url = _msca_validate_user_url(name)
    response = get_resource(url)
    return ValidatedUser().from_json(json.loads(response))


def _msca_validate_user_url(name):
    """
    Return UW MSCA uri for Office access validation
    """
    return "{}/ValidateUser?Name={}".format(url_base(), name)
