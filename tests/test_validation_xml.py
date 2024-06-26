# This file is part of CycloneDX Python Lib
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) OWASP Foundation. All Rights Reserved.

from glob import iglob
from os.path import join
from typing import Generator
from unittest import TestCase

from ddt import ddt, idata, unpack

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.schema import OutputFormat, SchemaVersion
from cyclonedx.validation.xml import XmlValidator
from tests import SCHEMA_TESTDATA_DIRECTORY, DpTuple

UNSUPPORTED_SCHEMA_VERSIONS = set()


def _dp(prefix: str) -> Generator:
    return (
        DpTuple((sv, tf)) for sv in SchemaVersion if sv not in UNSUPPORTED_SCHEMA_VERSIONS
        for tf in iglob(join(SCHEMA_TESTDATA_DIRECTORY, sv.to_version(), f'{prefix}-*.xml'))
    )


@ddt
class TestXmlValidator(TestCase):

    @idata(sv for sv in SchemaVersion if sv not in UNSUPPORTED_SCHEMA_VERSIONS)
    def test_validator_as_expected(self, schema_version: SchemaVersion) -> None:
        validator = XmlValidator(schema_version)
        self.assertIs(validator.schema_version, schema_version)
        self.assertIs(validator.output_format, OutputFormat.XML)

    @idata(UNSUPPORTED_SCHEMA_VERSIONS)
    def test_throws_with_unsupported_schema_version(self, schema_version: SchemaVersion) -> None:
        with self.assertRaisesRegex(ValueError, f'unsupported schema_version: {schema_version}'):
            XmlValidator(schema_version)

    @idata(_dp('valid'))
    @unpack
    def test_validate_no_none(self, schema_version: SchemaVersion, test_data_file: str) -> None:
        validator = XmlValidator(schema_version)
        with open(join(test_data_file), 'r') as tdfh:
            test_data = tdfh.read()
        try:
            validation_error = validator.validate_str(test_data)
        except MissingOptionalDependencyException:
            self.skipTest('MissingOptionalDependencyException')
        self.assertIsNone(validation_error)

    @idata(_dp('invalid'))
    @unpack
    def test_validate_expected_error(self, schema_version: SchemaVersion, test_data_file: str) -> None:
        validator = XmlValidator(schema_version)
        with open(join(test_data_file), 'r') as tdfh:
            test_data = tdfh.read()
        try:
            validation_error = validator.validate_str(test_data)
        except MissingOptionalDependencyException:
            self.skipTest('MissingOptionalDependencyException')
        self.assertIsNotNone(validation_error)
        self.assertIsNotNone(validation_error.data)
