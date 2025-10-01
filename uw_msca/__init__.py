# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with
the uwnetid subscription web service.
"""

import logging
from commonconf import settings
from restclients_core.exceptions import DataFailureException
from uw_msca.dao import MSCA_DAO


DAO = MSCA_DAO()
logger = logging.getLogger(__name__)


def url_base(override=None):
    # until msca api finalized
    return '/{}/{}'.format(
        override if override else 'prtmbx',
        getattr(settings, 'RESTCLIENTS_MSCA_VERSION', 'v1'))


def get_resource(url, headers=None):
    default_headers = {"Accept": "application/json"}
    if headers:
        default_headers.update(headers)

    response = DAO.getURL(url, default_headers)
    logger.debug("GET {0} ==status==> {1}".format(url, response.status))
    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

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


def put_resource(url, body, headers=None):
    default_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if headers:
        default_headers.update(headers)

    response = DAO.putURL(
        url,
        default_headers,
        body,
    )
    logger.debug("PUT {0} ==status==> {1}".format(url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug("PUT {0}s ==data==> {1}".format(url, response.data))

    return response.data


def patch_resource(url, body):
    response = DAO.patchURL(url, {
        'Content-Type': 'application/json',
        'Acept': 'application/json',
    }, body)
    logger.debug("PATCH {0} ==status==> {1}".format(url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug("PATCH {0}s ==data==> {1}".format(url, response.data))

    return response.data


def get_external_resource(url, body=None):
    response = DAO.get_external_resource(url, body=body)

    logger.debug(
        "external_resource {0} ==status==> {1}".format(url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug(
        "external_resource {0}s ==data==> {1}".format(url, response.data))

    return response.data
