# Copyright 2025 UW-IT, University of Washington
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
        return (
            valid
            if isinstance(valid, bool)
            else (
                (valid.lower() in ["true", "yes", "1"])
                if (isinstance(valid, str))
                else (valid != 0) if (isinstance(valid, int)) else False
            )
        )

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
            "delegate": self.delegate,
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
    drive_name = models.TextField()
    total_members = models.PositiveIntegerField()
    org_unit_id = models.SlugField(max_length=15)
    # e.g., "100 TB"; longest observed as of 2024-04-03 is 12 long
    org_unit_name = models.SlugField(max_length=20)
    member = models.SlugField(max_length=66)
    role = models.CharField(max_length=13)
    query_date = models.DateTimeField()
    total_uw_owners = models.PositiveIntegerField()
    size = models.PositiveIntegerField()

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
        "size_query_date",
    )

    CSV_FIELD_MAP = {
        "org_unitID": "org_unit_id",
        "org_unitName": "org_unit_name",
        "total_uwowners": "total_uw_owners"
    }

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

    @classmethod
    def from_csv(cls, csv_data: dict):
        """
        Factory for creating from CSV data from a csv.DictReader.
        """
        fields = dict([cls._map(k, v) for (k, v) in csv_data.items()])
        return cls(**fields)

    @classmethod
    def _map(cls, k, v):
        """
        Map CSV field name to model field name
        and CSV string value to appropriate model class value
        """
        if k not in cls.EXPECTED_CSV_FIELDS:
            raise ValueError(f"Unexpected field: {k}")

        try:
            field_name = cls.CSV_FIELD_MAP[k]
        except KeyError:
            field_name = k

        if 'Integer' in cls._field_class(field_name):
            try:
                field_value = int(v)
            except ValueError:
                field_value = 0
        else:
            field_value = v

        return field_name, field_value

    @classmethod
    def _field_class(cls, field_name):
        """
        Return the class name for the provided field name
        """
        try:
            return cls.__dict__[field_name].__class__.__name__
        except KeyError:
            return ''

    @classmethod
    def _int(cls, value):
        try:
            return int(value)
        except ValueError:
            return 0


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
