import os
from unittest import TestCase
from unittest.mock import (
    patch,
)

from commonconf import override_settings

from uw_msca.gdrive import (
    DAO,
    GoogleDriveState,
    get_google_drive_states,
)


@override_settings(
    RESTCLIENTS_MSCA_GDRIVE_OAUTH_TOKEN_URL="https://login.microsoftonline.com/example.uw.edu/oauth2/v2.0/token",
    RESTCLIENTS_MSCA_GDRIVE_REPORT_SCOPE="api://beef821f-dead-46ac-9829-f9a87eb12c37/.default",
    RESTCLIENTS_MSCA_GDRIVE_CLIENT_ID="beef821f-dead-46ac-9829-f9a87eb12c37",
    RESTCLIENTS_MSCA_GDRIVE_CLIENT_SECRET="my-secret",
    RESTCLIENTS_MSCA_GDRIVE_HOST="https://msca.hosts",
    RESTCLIENTS_MSCA_GDRIVE_DAO_CLASS="Mock",
)
class BaseGDriveTest(TestCase):
    "Base class for GDrive tests."
    abstract = True


class Test_MSCA_GDrive_DAO(BaseGDriveTest):
    def test_setting_host(self):
        "Mike figuring out the setting prefix is 'RESTCLIENTS_MSCA_GDRIVE_'"
        host = DAO.get_service_setting("HOST")
        assert host is not None

    def test_setting_ca_bundle(self):
        "Mike figuring out how to disable verification."
        ca_certs = DAO.get_setting("CA_BUNDLE", default="something")
        assert ca_certs is None


class Test_get_google_drive_states(BaseGDriveTest):
    def test(self):
        with patch.object(
            DAO,
            "get_external_resource",
            side_effect=[
                # returned after first call
                get_fixture("token_response_fixture"),
                # returned after second call
                get_fixture("report_response_fixture"),
                # further calls raise a StopIteration
            ],
        ):
            gdrive_states = get_google_drive_states()

        assert len(gdrive_states) == 3
        assert all(isinstance(X, GoogleDriveState) for X in gdrive_states)


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
