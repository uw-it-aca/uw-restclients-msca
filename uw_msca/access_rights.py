# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with UW MSCA outlook API
"""

import logging
import json
from uw_msca.models import AccessRight
from uw_msca import url_base, get_resource


logger = logging.getLogger(__name__)


def get_access_rights():
    """
    Returns list of Outlook mailbox Access Rights
    """
    url = _msca_access_rights_url()
    response = get_resource(url)
    return _json_to_supported(response)


def _msca_access_rights_url():
    """
    Return UW MSCA uri for Office access right resource
    """
    return f"{url_base()}/getaccesstypes"


def _json_to_supported(response_body):
    """
    Returns a list of Supported objects
    """
    data = json.loads(response_body)
    access_rights = []

    for access_right in data.get('value'):
        access_rights.append(AccessRight().from_json(access_right))

    return access_rights
