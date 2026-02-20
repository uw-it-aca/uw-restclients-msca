# Copyright 2026 UW-IT, University of Washington
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
    return (f"/{override if override else 'prtmbx'}/"
            f"{getattr(settings, 'RESTCLIENTS_MSCA_VERSION', 'v1')}")


def get_resource(url, headers=None):
    default_headers = {"Accept": "application/json"}
    if headers:
        default_headers.update(headers)

    response = DAO.getURL(url, default_headers)

    return _response("GET", url, response)


def post_resource(url, body):
    response = DAO.postURL(url, {
        'Content-Type': 'application/json',
        'Acept': 'application/json',
    }, body)

    return _response("POST", url, response)


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

    return _response("PUT", url, response)


def patch_resource(url, body):
    response = DAO.patchURL(url, {
        'Content-Type': 'application/json',
        'Acept': 'application/json',
    }, body)

    return _response("PATCH", url, response)


def get_external_resource(url, body=None):
    response = DAO.get_external_resource(url, body=body)

    return _response("external_resource", url, response)


def _response(method, url, response):
    logger.debug(f"{method} {url} ==status==> {response.status}")

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug(f"{method} {url} ==data==> {response.data}")

    return response.data
