# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from restclients_core import models


class ValidatedUser(models.Model):
    name = models.SlugField(max_length=32)
    valid = models.NullBooleanField()

    def is_valid(self):
        return self.valid

    def from_json(self, data):
        self.name = data["name"]
        self.valid = self._set_validity(data.get("valid"))
        return self

    def _set_validity(self, valid):
        """
        accept a range of truthy values and return a bool
        """
        return valid if isinstance(
            valid, bool) else (
                valid.lower() in ['true', 'yes', '1']) if (
                    isinstance(valid, str)) else (
                        valid != 0) if (
                            isinstance(valid, int)) else False

    def json_data(self):
        return {"name": self.name, "valid": self.valid}

    def __str__(self):
        return json.dumps(self.json_data())


class Delegate(models.Model):
    user = models.SlugField(max_length=32)
    delegate = models.SlugField(max_length=32)
    access_right = models.SlugField(max_length=32)

    def from_json(self, user, data):
        self.user = user
        self.delegate = data["User"]
        self.access_right = data["AccessRights"]
        return self

    def json_data(self):
        return {
            "user": self.user,
            "delegate": self.name,
            "access_right": self.access_right,
        }

    def __str__(self):
        return json.dumps(self.json_data())


class AccessRight(models.Model):
    right_id = models.SmallIntegerField()
    displayname = models.SlugField(max_length=32)

    def from_json(self, data):
        self.right_id = data.get("id")
        self.displayname = data.get("displayname")
        return self

    def json_data(self):
        return {"displayname": self.displayname, "id": self.right_id}

    def __str__(self):
        return json.dumps(self.json_data())


class GoogleDriveState(models.Model):
    # max_length values informed by examining all current results
    # TODO: more thorough solution
    drive_id = models.SlugField(max_length=19)
    drive_name = models.SlugField(max_length=125)
    total_members = models.PositiveIntegerField()
    org_unit_id = models.SlugField(max_length=15)
    # e.g., "100 TB"; longest observed as of 2024-04-03 is 12 long
    org_unit_name = models.SlugField(max_length=20)
    member = models.SlugField(max_length=66)
    role = models.CharField(max_length=13)
    query_date = models.DateTimeField()
    total_uw_owners = models.PositiveIntegerField()
    # TODO: where is size, size_capture_date, etc? clean up Mike!

    EXPECTED_CSV_FIELDS = (
        "id",
        "drive_id",
        "drive_name",
        "member",
        "role",
        "total_members",
        "total_uwowners",
        "org_unitID",
        "org_unitName",
        "query_date",
        "size",
        "file_count",
        "size_capture_date",
    )

    @classmethod
    def from_csv(cls, csv_data: dict):
        """
        Factory for creating from CSV data from a csv.DictReader.
        """
        drive_id = csv_data["drive_id"]
        drive_name = csv_data["drive_name"]
        member = csv_data["member"]
        role = csv_data["role"]
        total_members = csv_data["total_members"]
        total_uw_owners = csv_data["total_uwowners"]
        org_unit_id = csv_data["org_unitID"]
        org_unit_name = csv_data["org_unitName"]
        query_date = csv_data["query_date"]
        size = csv_data["size"]  # in MB
        file_count = csv_data["file_count"]
        # disappared from report; waiting for response from Ken on this
        # size_capture_date = csv_data["size_capture_date"]

        return cls(
            drive_id=drive_id,
            drive_name=drive_name,
            file_count=file_count,
            member=member,
            org_unit_id=org_unit_id,
            org_unit_name=org_unit_name,
            query_date=query_date,
            role=role,
            size=size,
            # size_capture_date=size_capture_date,
            total_members=total_members,
            total_uw_owners=total_uw_owners,
        )

    @property
    def quota_limit(self):
        return Quota.to_int(self.org_unit_name)

    @property
    def size_gigabytes(self):
        """
        Return size in GB.

        Native size field is in MB.
        """
        return self.size / 1024


class Quota:
    """
    Quota translation class.

    Quotas are implemented in the MSCA backend via Organization Units.

    Reporting from MSCA refers to this org unit instead so conversions must be
    easy.
    """

    # TODO: handle the "queued for deletion" OU name

    def to_str(quota: int):
        "Convert int quota from PRT to str quota MSCA uses internally."
        # TODO: type check / error?!
        return f"{quota}GB"

    def to_int(quota: str):
        "Convert a str quota for MSCA internal use to an int PRT can use."
        if not quota.endswith("GB"):
            raise ValueError(f"String {quota} does not end in 'GB'.")

        try:
            return int(quota[:-2])
        except ValueError:
            s = quota[:-2]
            if not s.isdigit():
                raise ValueError(f"Quota {quota} is not digits + 'GB' suffix")
            else:
                raise ValueError(f"Quota {quota} failed to convert {s} to int")
