"""Generate German translation files for GNU gettext.

- Update the project's 'de.po' translation file.
- Generate the language specific 'novelibre.mo' dictionary.

Usage: 
translate_de.py

File structure:

├── novxlib/
│   ├── i18n/
│   │   └── de.json
│   └── src/
│       ├── translations.py
│       └── msgfmt.py
└── <project>/
    ├── src/ 
    ├── tools/ 
    │   └── translate_de.py
    └── i18n/
        ├── messages.pot
        ├── de.po
        └── locale/
            └─ de/
               └─ LC_MESSAGES/
                  └─ novelibre.mo
    
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from shutil import copyfile
import translations
import msgfmt

APP_NAME = 'novxlib'
PO_PATH = '../i18n/de.po'
MO_PATH = '../i18n/locale/de/LC_MESSAGES/novelibre.mo'
MO_COPY = '../src/sample/locale/de/LC_MESSAGES/novelibre.mo'

if translations.main('de', app=APP_NAME):
    print(f'Writing "{MO_PATH}" ...')
    msgfmt.make(PO_PATH, MO_PATH)
    copyfile(MO_PATH, MO_COPY)
