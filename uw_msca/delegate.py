# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UW MSCA outlook API
"""

from uw_msca.models import Delegate
from uw_msca import (url_base, get_resource, post_resource,
                     patch_resource, get_external_resource)
from restclients_core.exceptions import DataFailureException
import json
import logging


logger = logging.getLogger(__name__)


def _delegate_url_base(netid):
    """
    Return UW MSCA base uri for Office access delegates
    """
    return f"{url_base()}/{netid}"


def _msca_get_delegates_url(netid):
    """
    Return UW MSCA uri for Office access delegates
    """
    return f"{_delegate_url_base(netid)}/getdelegates"


def _msca_get_all_delegates_csv_url():
    """
    Return UW MSCA uri for Office all access delegates
    """
    return f"{url_base()}/getdelegatecsv"


def _msca_set_delegate_url(netid, delegate, access_type):
    """
    Return UW MSCA uri to set delegate access
    """
    return (f"{_delegate_url_base(netid)}/setdelegateperms/"
            f"{delegate}/{access_type}")


def _msca_update_delegate_url(netid, delegate, old_access_type, access_type):
    """
    Return UW MSCA uri to set delegate access
    """
    return (f"{_delegate_url_base(netid)}/updatedelegateperms/"
            f"{delegate}/{old_access_type}/{access_type}")


def _msca_remove_delegate_url(netid, delegate, access_type):
    """
    Return UW MSCA uri for removing delegate access
    """
    return (f"{_delegate_url_base(netid)}/removedelegateperms/"
            f"{delegate}/{access_type}")


def get_delegates(netid):
    """
    Returns delegate list for given netid, mind payload changes
    """
    url = _msca_get_delegates_url(netid)
    response = get_resource(url)

    try:
        data = json.loads(response)
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
        elif not isinstance(data, dict):
            raise Exception("unexpected data: {data}")

        mailbox = data['TargetNetid']
        delegates = data['Delegates']
        if netid == mailbox:
            return [Delegate().from_json(mailbox, d) for d in delegates]

        logger.error(
            f"get_delegates: netid mismatch: {netid} != {mailbox}")
    except (KeyError, json.JSONDecodeError) as ex:
        logger.error(
            f"get_delegates: malformed response: {response}")
    except DataFailureException as ex:
        if ex.status in [202, 400, 404]:
            data = json.loads(ex.msg)
            logger.info(f"get_delegates ({ex.status}): {netid}: "
                        f"{data.get('msg'), 'Unreported MSCA error'}")
        elif ex.status == 500:
            logger.info(
                f"get_delegates (500): Azure/Exchange API error, retrying")
        else:
            raise

    return []


def get_all_delegates():
    """
    method returns all delegations assigned in outlook via
    two sequence request.  first, request url for all delegate csv.
    second, request csv from url returned in first request.
    from: https://pplat-apimgmt.azure-api.net/mbx/v1/GetDelegateCsv
    """
    try:
        delegates_csv_url = _msca_get_all_delegates_csv_url()
        response = get_resource(delegates_csv_url)
        data = json.loads(response)
        csv_url = data['sasUrl']
        logger.info(f"get_all_delegates: url: {csv_url}")

        response = get_external_resource(csv_url)
        return response.decode('utf-8').split('\r\n')
    except json.JSONDecodeError:
        logger.error(f"get_all_delegates: Malformed URL response {response}")
    except KeyError:
        logger.error(f"get_all_delegates: Malformed URL response {data}")


def set_delegate(netid, delegate, access_type):
    """
    Returns with delegate access set for netid resource
    """
    url = _msca_set_delegate_url(netid, delegate, access_type)
    body = json.dumps({
        'netid': netid,
        'delegate': delegate,
        'accesstype': access_type
    })

    response = post_resource(url, body)

    try:
        json_response = json.loads(response)
        return Delegate(user=json_response['Netid'],
                        delegate=json_response['Delegate'],
                        access_right=json_response['SetAccessType'])
    except DataFailureException as ex:
        raise
    except Exception as ex:
        logger.error(f"set_delegate: {ex}")
        raise


def update_delegate(netid, delegate, old_access_type, new_access_type):
    """
    Returns with delegate access set for netid resource
    """
    url = _msca_update_delegate_url(
        netid, delegate, old_access_type, new_access_type)
    body = json.dumps({
        'netid': netid,
        'delegate': delegate,
        'RemoveAccesstype': old_access_type,
        'SetAccesstype': new_access_type,
    })

    try:
        response = patch_resource(url, body)
        json_response = json.loads(response)
        return Delegate(user=json_response['Netid'],
                        delegate=json_response['Delegate'],
                        access_right=json_response['SetAccessType'])
    except DataFailureException as ex:
        raise
    except Exception as ex:
        logger.error(f"update_delegate: {ex}")
        raise


def remove_delegate(netid, delegate, access_type):
    """
    Returns with delegate access removed from netid resource
    """
    url = _msca_remove_delegate_url(netid, delegate, access_type)
    body = json.dumps({
        'netid': netid,
        'delegate': delegate,
        'removeaccesstype': access_type
    })

    try:
        response = post_resource(url, body)
        json_response = json.loads(response)
        return Delegate(user=json_response['Netid'],
                        delegate=json_response['Delegate'],
                        access_right=json_response['Removed AccessType'])
    except DataFailureException as ex:
        raise
    except Exception as ex:
        logger.error(f"remove_delegate: {ex}")
        raise
