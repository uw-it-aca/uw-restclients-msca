# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with
the uwnetid subscription web service.
"""

import logging
import json
from commonconf import settings
from restclients_core.exceptions import DataFailureException
from uw_msca.dao import MSCA_DAO


DAO = MSCA_DAO()
logger = logging.getLogger(__name__)


def url_base():
    return ""
    return '/outlook/{}'.format(
        getattr(settings, 'RESTCLIENTS_MSCA_VERSION', 'v1'))


def get_resource(url):
    response = DAO.getURL(url, {'Accept': 'application/json'})
    logger.debug("GET {0} ==status==> {1}".format(url, response.status))
    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    _test_for_invalid_user(url, response.data)

    logger.debug("GET {0} ==data==> {1}".format(url, response.data))

    return response.data


def post_resource(url, body):
    response = DAO.postURL(url, {
        'Content-Type': 'application/json',
        'Acept': 'application/json',
    }, body)
    logger.debug("POST {0} ==status==> {1}".format(url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug("POST {0}s ==data==> {1}".format(url, response.data))

    return response.data