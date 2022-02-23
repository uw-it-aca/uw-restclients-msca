# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from restclients_core import models
from dateutil.parser import parse


class ValidatedUser(models.Model):
    name = models.SlugField(max_length=32)
    valid = models.NullBooleanField()

    def is_valid(self):
        return self.valid == True

    def from_json(self, data):
        self.name = data['name']
        self.valid = data.get('valid') == "true"
        return self

    def json_data(self):
        return {'name': self.name,
                'valid': self.valid}

    def __str__(self):
        return json.dumps(self.json_data())


class AccessType(models.Model):
    code = models.SmallIntegerField()
    name = models.SlugField(max_length=32)

    def from_json(self, data):
        self.code = data.get('code')
        self.name = data['name']
        return self

    def json_data(self):
        return {'name': self.name,
                'code': self.code}

    def __str__(self):
        return json.dumps(self.json_data())
