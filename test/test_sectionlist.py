"""Regression test for novelibre file processing.

Test the conversion of the sections list.

For further information see https://github.com/peter88213/novelibre
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from nvlib.model.ods.ods_w_sectionlist import OdsWSectionList
from novxlib.test.import_export_test import ExportTest
import unittest


class NrmOpr(ExportTest, unittest.TestCase):
    _exportClass = OdsWSectionList

    # The test methods must be defined here to identify the source of failure.

    def test_novx_to_exp(self):
        super().test_novx_to_exp()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
