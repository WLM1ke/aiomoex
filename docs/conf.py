# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys


sys.path.insert(0, os.path.abspath('../'))

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinxcontrib.asyncio'
]
autodoc_member_order = 'bysource'
templates_path = ['templates']

source_suffix = '.rst'
master_doc = 'index'
project = 'aiomoex'
copyright = '2018, Mikhail Korotkov aka WLMike'
author = 'Mikhail Korotkov aka WLMike'
# The short X.Y version
version = ''
release = '1.0.0'
language = 'ru'
exclude_patterns = ['build']
highlight_language = 'default'
html_theme = 'aiohttp_theme'

html_theme_options = {
    'logo': '',
    'description': 'Asyncio MOEX ISS API',
    'canonical_url': 'https://wlm1ke.github.io/aiomoex',
    'github_user': 'WLM1ke',
    'github_repo': 'aiomoex',
    'github_button': False,
    'github_type': '',
    'github_banner': True,
    'travis_button': True,
    'badges': [{'image': 'https://api.codacy.com/project/badge/Coverage/363c10e1d85b404882326cf62b78f25c',
                'target': 'https://app.codacy.com/project/wlmike/aiomoex/dashboard',
                'height': '20',
                'alt': 'Code coverage status'},
               {'image': 'https://badge.fury.io/py/aiomoex.svg',
                'target': 'https://badge.fury.io/py/aiomoex',
                'height': '20',
                'alt': 'Latest PyPI package version'}
               ],
    'sidebar_collapse': False
}

html_static_path = ['static']

html_sidebars = {
    "**": [
        'about.html',
        'navigation.html'
    ]
}
