import contextlib
import csv
import os
from unittest import TestCase
from unittest.mock import (
    call,
    patch,
    sentinel,
)
from urllib.parse import urlencode

from commonconf import settings

from uw_msca.gdrive import (
    GoogleDriveReport,
    DAO,
    get_google_drive_states,
)


class Test_MSCA_GDrive_DAO(TestCase):
    def test_setting_host(self):
        "Mike figuring out the setting prefix is 'RESTCLIENTS_MSCA_GDRIVE_'"
        host = DAO.get_service_setting("HOST")
        assert host is not None

    def test_setting_ca_bundle(self):
        "Mike figuring out how to disable verification."
        ca_certs = DAO.get_setting("CA_BUNDLE", default="something")
        assert ca_certs is None


@contextlib.contextmanager
def setup_fixtures_manually():
    """
    Sets up fixture state for two cases.
    """
    in_order_returns = [
        # returned after first call
        get_fixture("token_response_fixture"),
        # returned after second call
        get_fixture("report_response_fixture"),
        # further calls raise a StopIteration
    ]

    with (
        # patch this to simplify testing
        patch.object(
            GoogleDriveReport,
            "_get_bearer_token_body",
            return_value=sentinel.BEARER_TOKEN_BODY,
        ),
        # patch this to use mocked responses by call order
        patch.object(
            DAO,
            "get_external_resource",
            side_effect=in_order_returns,
        ) as get_external_resource,
    ):
        yield get_external_resource


class GoogleDriveStateListTest(TestCase):
    def test_get_google_drive_states(self):
        with setup_fixtures_manually():
            gdrive_states = get_google_drive_states()

        assert len(gdrive_states) == 3


class GoogleDriveReportTest(TestCase):
    def setUp(self):
        self.instance = GoogleDriveReport()

    def test_main(self):
        with setup_fixtures_manually() as get_external_resource:
            resp = self.instance.main()

        assert isinstance(resp, csv. DictReader)

        assert get_external_resource.call_count == 2
        call1, call2 = get_external_resource.call_args_list

        assert call1 == call(
            settings.RESTCLIENTS_MSCA_GDRIVE_OAUTH_TOKEN_URL,
            body=sentinel.BEARER_TOKEN_BODY,
        )
        sas_key = "https://pplatreports.blob.core.windows.net/example-url"
        assert call2 == call(sas_key)

    def test_get_bearer_token_body(self):
        secret = "my-secret"
        expected_data = {
            "client_id": settings.RESTCLIENTS_MSCA_GDRIVE_CLIENT_ID,
            "client_secret": secret,
            "grant_type": "client_credentials",
            "scope": settings.RESTCLIENTS_MSCA_GDRIVE_REPORT_SCOPE,
        }
        expected = urlencode(expected_data)
        with patch.object(
            settings,
            "RESTCLIENTS_MSCA_GDRIVE_CLIENT_SECRET",
            secret,
        ):
            actual = self.instance._get_bearer_token_body()
        assert actual == expected


def get_fixture(name):
    tests_dir = os.path.abspath(os.path.dirname(__file__))
    resource_dir = os.path.join(tests_dir, "../resources")
    # TODO: inject the dao IFF this doesn't all quickly fold to one host
    service_name = "msca_gdrive"
    implementation_name = "file"
    from restclients_core.util.mock import load_resource_from_path

    return load_resource_from_path(
        resource_dir,
        service_name,
        implementation_name,
        url="/" + name,
        headers=None,
    )
