"""Convert yw7 projects to novx.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/yw2novx
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys
import os
import glob

from novxlib.yw.yw7_file import Yw7File
from novxlib.novx.novx_file import NovxFile
from novxlib.model.novel import Novel
from novxlib.model.nv_tree import NvTree

TEST_DATA_PATH = '../test/data'


def convert_yw7_file(sourcePath):
    path, extension = os.path.splitext(sourcePath)
    if extension != '.yw7':
        print(f'Error: File must be .yw7 type, but is "{extension}".')
        return

    targetPath = f'{path}.novx'
    source = Yw7File(sourcePath)
    target = NovxFile(targetPath)
    source.novel = Novel(tree=NvTree())
    source.read()
    target.novel = source.novel
    target.write()
    print('Done')


def convert_test_data(testDataPath):
    for module in glob.iglob(f'{testDataPath}/**/*.yw7', recursive=True):
        sourcePath = module.replace("\\", "/")
        print(sourcePath)
        convert_yw7_file(sourcePath)


if __name__ == '__main__':
    try:
        convert_yw7_file(sys.argv[1])
    except IndexError:
        convert_test_data(TEST_DATA_PATH)

