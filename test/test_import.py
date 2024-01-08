"""Regression test for noveltree file processing.

Test the import of a work in progress.

For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.odt.odt_r_import import OdtRImport
from novxlib.test.import_test import ImportTest
import unittest


class NrmOpr(ImportTest, unittest.TestCase):
    _importClass = OdtRImport
    _dataPath = '../test/data/_import/'

    # The test methods must be defined here to identify the source of failure.

    def test_imp_to_novx(self):
        super().test_imp_to_novx()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
