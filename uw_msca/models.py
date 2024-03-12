# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from restclients_core import models


class ValidatedUser(models.Model):
    name = models.SlugField(max_length=32)
    valid = models.NullBooleanField()

    def is_valid(self):
        return self.valid

    def from_json(self, data):
        self.name = data['name']
        self.valid = data.get('valid', '') == "true"
        return self

    def json_data(self):
        return {'name': self.name,
                'valid': self.valid}

    def __str__(self):
        return json.dumps(self.json_data())


class Delegate(models.Model):
    user = models.SlugField(max_length=32)
    delegate = models.SlugField(max_length=32)
    access_right = models.SlugField(max_length=32)

    def from_json(self, user, data):
        self.user = user
        self.delegate = data['User']
        self.access_right = data['AccessRights']
        return self

    def json_data(self):
        return {'user': self.user,
                'delegate': self.name,
                'access_right': self.access_right}

    def __str__(self):
        return json.dumps(self.json_data())


class AccessRight(models.Model):
    right_id = models.SmallIntegerField()
    displayname = models.SlugField(max_length=32)

    def from_json(self, data):
        self.right_id = data.get('id')
        self.displayname = data.get('displayname')
        return self

    def json_data(self):
        return {'displayname': self.displayname,
                'id': self.right_id}

    def __str__(self):
        return json.dumps(self.json_data())


class GoogleDriveState(models.Model):
    # max_length values informed by examining all current results
    # TODO: more thorough solution
    drive_id = models.SlugField(max_length=19)
    drive_name = models.SlugField(max_length=125)
    total_members = models.PositiveIntegerField()
    org_unit = models.SlugField(max_length=15)
    member = models.SlugField(max_length=66)
    role = models.CharField(max_length=13)
    query_date = models.DateTimeField()
