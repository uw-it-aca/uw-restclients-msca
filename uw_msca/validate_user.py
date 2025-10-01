# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UW MSCA outlook API
"""

from uw_msca.models import ValidatedUser
from uw_msca import url_base, get_resource
from restclients_core.exceptions import DataFailureException
import logging
import json


logger = logging.getLogger(__name__)


def validate_user(name):
    """
    Returns whether or not given user has access to Outlook mailbox
    """
    is_valid = False
    try:
        url = _msca_validate_user_url(name)
        response = get_resource(url)
        # 200 response means user exists and is valid
        is_valid = True
    except DataFailureException as ex:
        if ex.status in [400, 404]:
            data = json.loads(ex.msg)
            logger.info(f"validate_user ({ex.status}): {name}: "
                        f"{data.get('msg'), 'Unreported MSCA error'}")
        else:
            raise

    return ValidatedUser(name=name, valid=is_valid)


def _msca_validate_user_url(name):
    """
    Return UW MSCA uri for Office access validation
    """
    return f"{url_base()}/validateuser/{name}"
