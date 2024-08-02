"""Helper module for novelibre application and plugin building. 

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
from shutil import copy2
from shutil import make_archive
import zipapp

import inliner
import pgettext


def collect_dist_files(distFiles):
    for file, targetDir in distFiles:
        os.makedirs(targetDir, exist_ok=True)
        print(f'Copying "{file}" to "{targetDir}" ...')
        copy2(file, targetDir)


def inline_modules(source, target):
    """Inline all non-standard library modules."""
    NVLIB = 'nvlib'
    NV_PATH = '../../novelibre/src/'
    NOVXLIB = 'novxlib'
    NOVX_PATH = '../../novxlib/src/'
    inliner.run(source, target, NVLIB, NV_PATH)
    inliner.run(target, target, NOVXLIB, NOVX_PATH)


def insert_version_number(source, version='unknown'):
    """Write the actual version string and make sure that Unix EOL is used."""
    with open(source, 'r', encoding='utf_8') as f:
        lines = f.read()
    newlines = []
    for line in lines.split('\n'):
        newlines.append(line.replace('@release', version))
    with open(source, 'w', encoding='utf_8', newline='\n') as f:
        f.write('\n'.join(newlines))
    print(f'Version {version} set.')


def make_pot(sourcefile, app='', version='unknown'):
    """Generate a pot file for translations from the source file."""
    I18_DIR = '../i18n'
    POT_FILE = f'{I18_DIR}/messages.pot'
    os.makedirs(I18_DIR, exist_ok=True)
    if os.path.isfile(POT_FILE):
        os.replace(POT_FILE, f'{POT_FILE}.bak')
        backedUp = True
    else:
        backedUp = False
    try:
        pot = pgettext.PotFile(POT_FILE, app=app, appVersion=version)
        pot.scan_file(sourcefile)
        print(f'Writing "{pot.filePath}"...\n')
        pot.write_pot()
        return True

    except Exception as ex:
        if backedUp:
            os.replace(f'{POT_FILE}.bak', POT_FILE)
        print(str(ex))
        return False


def make_pyz(sourceDir, targetDir, release):
    targetFile = f'{targetDir}/{release}.pyzw'
    print(f'Writing "{targetFile}" ...')
    zipapp.create_archive(
        sourceDir,
        targetFile,
        main='setuplib:main',
        compressed=True
        )


def make_zip(sourceDir, targetDir, release):
    copy2('../src/setup.pyw', sourceDir)
    copy2('../docs/usage.md', f'{sourceDir}/README.md')
    target = f'{targetDir}/{release}'
    print(f'Writing "{target}.zip" ...')
    make_archive(target, 'zip', sourceDir)

