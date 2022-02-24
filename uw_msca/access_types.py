# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with UW MSCA outlook API
"""

import logging
import json
from uw_msca.models import AccessType
from uw_msca import url_base, get_resource


logger = logging.getLogger(__name__)


def get_access_types():
    """
    Returns list of Outlook mailbox Access Types
    """
    url = _msca_access_types_url()
    response = get_resource(url)
    return _json_to_supported(response)


def _msca_access_types_url():
    """
    Return UW MSCA uri for Office access type resource
    """
    return "{}/GetAccessRights".format(url_base())


def _json_to_supported(response_body):
    """
    Returns a list of Supported objects
    """
    data = json.loads(response_body)
    access_types = []

    for access_type in data:
        access_types.append(AccessType().from_json(access_type))

    return access_types
