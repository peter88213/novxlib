"""Regression test for noveltree file processing.

Test the conversion of the item list.

For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.ods.ods_r_itemlist import OdsRItemList
from novxlib.ods.ods_w_itemlist import OdsWItemList
from novxlib.test.import_export_test import ImportExportTest
import unittest


class NrmOpr(ImportExportTest, unittest.TestCase):
    _importClass = OdsRItemList
    _exportClass = OdsWItemList

    # The test methods must be defined here to identify the source of failure.

    def test_novx_to_exp(self):
        super().test_novx_to_exp()

    def test_imp_to_novx(self):
        super().test_imp_to_novx()

    def test_data(self):
        super().test_data()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
