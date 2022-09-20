# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UW MSCA outlook API
"""

from uw_msca.models import Delegate
from uw_msca import url_base, get_resource, post_resource
from urllib import parse
import json
import logging


logger = logging.getLogger(__name__)


def get_delegates(netid):
    """
    Returns whether or not given user has access to Outlook mailbox
    """
    url = _msca_get_delegate_url(netid)
    response = get_resource(url)

    json_response = json.loads(response)
    user = json_response['TargetNetid']
    delegates = []
    for delegate in json_response['Delegates']:
        delegates.append(Delegate().from_json(user, delegate))

    return delegates


def _msca_get_delegate_url(netid):
    """
    Return UW MSCA uri for Office access delegates
    """
    return "{}/GetDelegates?netid={}".format(url_base(), netid)


def set_delegate(netid, delegate, access_type):
    """
    Returns with delegate access set for netid resource
    """
    url = _msca_set_delegate_url()
    params = {
        netid: netid,
        delegate: delegate,
        access_type: access_type
    }

    response = post_resource(url, parse.urlencode(params))

    json_response = json.loads(response)
    user = json_response['TargetNetid']
    delegates = []
    for delegate in json_response['Delegates']:
        delegates.append(Delegate().from_json(user, delegate))

    return delegates


def _msca_set_delegate_url():
    """
    Return UW MSCA uri to set delegate access
    """
    return "{}/SetDelegatePerms".format(url_base())


def remove_delegate(netid, delegate, access_type):
    """
    Returns with delegate access removed from netid resource
    """
    url = _msca_remove_delegate_url()
    params = {
        netid: netid,
        delegate: delegate,
        access_type: access_type
    }

    response = post_resource(url, parse.urlencode(params))

    json_response = json.loads(response)
    user = json_response['TargetNetid']
    delegates = []
    for delegate in json_response['Delegates']:
        delegates.append(Delegate().from_json(user, delegate))

    return delegates


def _msca_remove_delegate_url(netid, delegate, access_type):
    """
    Return UW MSCA uri for removing delegate access
    """
    return "{}/RemoveDelegatePerms?netid={}?delegate={}&accesstype={}".format(
        url_base(), netid, delegate, access_type)
