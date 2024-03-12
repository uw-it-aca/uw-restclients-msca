import csv
import json
import os
from urllib.parse import urlencode

from urllib3 import PoolManager
from urllib3.util.retry import Retry

from restclients_core.dao import DAO
from restclients_core.exceptions import DataFailureException
from uw_msca import (
    logger,
    url_base,
)


class MSCA_GDrive_DAO(DAO):
    """
    MSCA client for Google Drive things.
    """
    def service_name(self):
        return 'msca_gdrive'

    def service_mock_paths(self):
        return [os.path.abspath(os.path.join(os.path.dirname(__file__), "resources"))]  # noqa

    # modified to allow a body arg
    def getURL(self, url, headers={}, body=None):
        return self._load_resource("GET", url, headers, body)

    def get_external_resource(self, url, **kwargs):
        http = PoolManager(
            retries=Retry(total=1, connect=0, read=0, redirect=1))
        return http.request('GET', url, **kwargs)


DAO = MSCA_GDrive_DAO()


# copy/pasted from __init__ to use the correct DAO global
# updated to include headers arg
def get_resource(url, headers=None):
    default_headers = {'Accept': 'application/json'}
    if headers:
        default_headers.update(headers)

    response = DAO.getURL(url, default_headers)
    logger.debug("GET {0} ==status==> {1}".format(url, response.status))
    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug("GET {0} ==data==> {1}".format(url, response.data))

    return response.data


# copy/pasted from __init__ to use the correct DAO global
# updated to include kwargs (body)
def get_external_resource(url, **kwargs):
    response = DAO.get_external_resource(url, **kwargs)

    logger.debug(
        "external_resource {0} ==status==> {1}".format(url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug(
        "external_resource {0}s ==data==> {1}".format(url, response.data))

    return response.data


class GoogleDriveReport:
    """
    Responsible for getting the report of the current shared drive state.
    """
    def main(self):
        body = self._get_bearer_token_body()
        token_response = get_external_resource(
            DAO.get_service_setting("OAUTH_TOKEN_URL"),
            body=body,
        )
        token = json.loads(token_response)['access_token']

        latest_report_url_response = get_resource(
            DAO.get_service_setting("LATEST_REPORT_URL"),
            headers={"Authorization": f"Bearer {token}"},
        )

        latest_report_url = json.loads(latest_report_url_response)['sasKey']  # noqa

        # TODO: stream response via a header?
        report_resp = get_external_resource(latest_report_url)
        # TODO: define a proper model for this
        return csv.DictReader(report_resp.decode())

    def _get_bearer_token_body(self):
        data = {
            "client_id": DAO.get_service_setting("CLIENT_ID"),
            "client_secret": DAO.get_service_setting("CLIENT_SECRET"),
            "grant_type": "client_credentials",
            "scope": DAO.get_service_setting("REPORT_SCOPE"),
        }
        body = urlencode(data)
        return body


def _msca_drive_base_url():
    """
    TODO: confirm with Ken S. that the URLs will be versioned
    """
    base = url_base(override="drive")
    # remove version component of path until TODO is resolved
    result, version = base.rsplit("/", 1)
    return result
