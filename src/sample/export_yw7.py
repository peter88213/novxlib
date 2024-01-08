"""Convert novx to yw7.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/yw2novx
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys
import os
from novxlib.yw.yw7_file import Yw7File
from novxlib.novx.novx_file import NovxFile
from novxlib.model.novel import Novel
from novxlib.model.nv_tree import NvTree
SUFFIX = ''


def main(sourcePath):
    path, extension = os.path.splitext(sourcePath)
    if extension != '.novx':
        print(f'Error: File must be .novx type, but is "{extension}".')
        return

    targetPath = f'{path}.yw7'
    source = NovxFile(sourcePath)
    target = Yw7File(targetPath)
    source.novel = Novel(tree=NvTree())
    source.read()
    target.novel = source.novel
    target.wcLog = source.wcLog
    target.write()
    print('Done')


if __name__ == '__main__':
    main(sys.argv[1])
