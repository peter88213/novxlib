"""Regression test for novelibre file processing.

Test the conversion of the section descriptions.

For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.odt.odt_r_sectiondesc import OdtRSectionDesc
from novxlib.odt.odt_w_sectiondesc import OdtWSectionDesc
from novxlib.test.import_export_test import ImportExportTest
import unittest


class NrmOpr(ImportExportTest, unittest.TestCase):
    _importClass = OdtRSectionDesc
    _exportClass = OdtWSectionDesc

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
