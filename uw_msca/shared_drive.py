# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
"""
This file contains the interfaces for MSCA's /google/vN/drive endpoints.

Of note, maximum drive disk quota is not well supported by Google. At this time
of writing support was provided only via the Organization Unit (OU) the drive
is located in.
"""

import csv
import io
import json
import logging
from urllib.parse import urlencode

from uw_msca import (
    DAO,
    url_base,
    get_resource,
    get_external_resource,
    put_resource,
)

from uw_msca.models import (
    GoogleDriveState,
    Quota,
)


def get_default_org_unit():
    """
    Return the default/subsidized Org Unit for Shared Drives.
    """
    org_unit_resp = get_resource(
        url=_get_default_org_unit_url(),
        headers=_authorization_headers(),
    )
    j = json.loads(org_unit_resp)
    return j["ou"]


def get_default_quota():
    default_quota: str = get_default_org_unit()
    return Quota.to_int(default_quota)


def get_google_drive_states():
    """
    Return list of GoogleDriveState's from report generated by PPLAT.
    """
    drive_state_reports_resp = get_resource(
        url=_get_drivestate_url(),
        headers=_authorization_headers(),
    )

    drive_state_reports_url = json.loads(drive_state_reports_resp)["sasKey"]
    report_resp: bytes = get_external_resource(drive_state_reports_url)

    # wrap encoded bytes such that they can be iterated over per-line
    filelike = io.TextIOWrapper(io.BytesIO(report_resp))

    records = csv.DictReader(filelike)
    if not set(records.fieldnames).issuperset(
        GoogleDriveState.EXPECTED_CSV_FIELDS
    ):
        missing = [
            X
            for X in GoogleDriveState.EXPECTED_CSV_FIELDS
            if X not in records.fieldnames
        ]
        logging.error(
            f"Missing expected fields from {_get_drivestate_url()}: {missing}"
        )

    result = []

    for record in records:
        result.append(GoogleDriveState.from_csv(record))

    return result


def set_drive_quota(quota: int, drive_id: str):
    """
    Update Google Drive to have the specified quota.

    Args:
        quota: integer quota in units of GB. 100 == 100GB

    Raises:
        ValueError: quota is non-integer value.
    """
    str_quota = Quota.to_str(quota)

    # in this case quota values are implicitly provided by the
    # Organizational Unit (OU) of the drive
    # so what we're really doing is moving a drive between OUs
    data = {"quota": str_quota}

    resp_data = put_resource(
        url=_set_quota_url(drive_id),
        body=json.dumps(data),
        headers=_authorization_headers(),
    )

    try:
        # Mike asked for a JSON payload
        return json.loads(resp_data)
    except json.JSONDecodeError:
        # until Ken delivers change
        result = resp_data.decode()
        return {"message": result}


def _set_quota_url(drive_id):
    return f"{_msca_drive_base_url()}/{drive_id}/setquota"


def _get_default_org_unit_url():
    return f"{_msca_drive_base_url()}/defaultou"


def _get_drivestate_url():
    return f"{_msca_drive_base_url()}/getfile"


def _msca_drive_base_url():  # returns "/google/v1/drive"
    base = url_base(override="google")
    return f"{base}/drive"


def _authorization_headers():
    """
    Get OAuth bearer token for authorization in subsequent requests.
    """
    data = {
        "client_id": DAO.get_service_setting("CLIENT_ID"),
        "client_secret": DAO.get_service_setting("CLIENT_SECRET"),
        "grant_type": "client_credentials",
        "scope": DAO.get_service_setting("REPORT_SCOPE"),
    }
    body = urlencode(data)

    token_response = get_external_resource(
        DAO.get_service_setting("OAUTH_TOKEN_URL"),
        body=body,
    )
    token = json.loads(token_response)["access_token"]

    auth_headers = {"Authorization": f"Bearer {token}"}

    return auth_headers