# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from unittest.mock import (
    patch,
)

from commonconf import override_settings

from uw_msca.shared_drive import (
    DAO,
    GoogleDriveState,
    get_default_org_unit,
    get_default_quota,
    get_google_drive_states,
    set_drive_quota,
    _msca_drive_base_url,
)


@override_settings(
    RESTCLIENTS_MSCA_OAUTH_TOKEN_URL=(
        "https://login.microsoftonline.com/example.uw.edu/oauth2/v2.0/token",
    ),
    RESTCLIENTS_MSCA_REPORT_SCOPE=(
        "api://beef821f-dead-46ac-9829-f9a87eb12c37/.default"
    ),
    RESTCLIENTS_MSCA_CLIENT_ID="beef821f-dead-46ac-9829-f9a87eb12c37",
    RESTCLIENTS_MSCA_CLIENT_SECRET="my-secret",
    RESTCLIENTS_MSCA_HOST="https://msca.hosts",
    RESTCLIENTS_MSCA_SUBSCRIPTION_KEY="my-subscription-key",
    RESTCLIENTS_MSCA_DAO_CLASS="Mock",
)
class BaseGDriveTest(TestCase):
    "Base class for GDrive tests."
    abstract = True


class Test_MSCA_GDrive(BaseGDriveTest):
    def test_msca_drive_base_url(self):
        assert _msca_drive_base_url() == "/google/v1/drive"


class Test_get_default_org_unit(BaseGDriveTest):
    def test(self):
        with patch.object(
            DAO,
            "get_external_resource",
            side_effect=[
                # returned after first call
                DAO.getURL("/google/token_response_fixture"),
                # further calls raise a StopIteration
            ],
        ):
            result = get_default_org_unit()
        assert result == "100GB"


class Test_get_default_quota(BaseGDriveTest):
    def test(self):
        with patch.object(
            DAO,
            "get_external_resource",
            side_effect=[
                # returned after first call
                DAO.getURL("/google/token_response_fixture"),
                # further calls raise a StopIteration
            ],
        ):
            result = get_default_quota()
        assert result == 100


class Test_get_google_drive_states(BaseGDriveTest):
    def test(self):
        with patch.object(
            DAO,
            "get_external_resource",
            side_effect=[
                # returned after first call
                DAO.getURL("/google/token_response_fixture"),
                # returned after second call
                DAO.getURL("/google/report_response_fixture"),
                # further calls raise a StopIteration
            ],
        ):

            gdrive_states = get_google_drive_states()

        assert len(gdrive_states) == 3
        assert all(isinstance(X, GoogleDriveState) for X in gdrive_states)
        assert gdrive_states[0].org_unit_name == "uw.edu"
        assert gdrive_states[0].org_unit_id == "00gjdgxs0123458"
        assert gdrive_states[0].total_uw_owners == 2
        assert gdrive_states[0].size == 307


class Test_set_drive_quota(BaseGDriveTest):
    def test(self):
        drive_id = "0AIdwn8Py42DEADBEEF"
        quota = 3000
        with patch.object(
            DAO,
            "get_external_resource",
            side_effect=[
                DAO.getURL("/google/token_response_fixture"),
            ],
        ):
            result = set_drive_quota(quota=quota, drive_id=drive_id)

        assert result == {
            "message": f"Drive '{drive_id}' successfully moved to 3000GB"
        }
