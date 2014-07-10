# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

'''ftrack connect documentation build configuration file.'''

import sys
import os

# -- General ------------------------------------------------------------------

# Extensions.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode'
]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_extension'))
extensions.append('auto_domain_summary')

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'ftrack connect'
copyright = u'2014, ftrack'

# Version.
# TODO: Read version from config.
_version = 'dev'
version = _version
release = _version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_template', '_theme', '_extension']

# A list of prefixes to ignore for module listings.
modindex_common_prefix = ['ftrack.']

# -- HTML output --------------------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_path = ['_theme']
html_static_path = ['_static']
html_style = 'ftrack.css'

html_theme_options = {
    'sticky_navigation': True,
}

# If True, copy source rst files to output for reference.
html_copy_source = True


# -- Autodoc ------------------------------------------------------------------

autodoc_default_flags = ['members', 'undoc-members', 'inherited-members']


def autodoc_skip(app, what, name, obj, skip, options):
    '''Don't skip __init__ method for autodoc.'''
    if name == '__init__':
        return False

    return skip


# -- Intersphinx --------------------------------------------------------------

intersphinx_mapping = {'python': ('http://docs.python.org/', None)}


# -- Setup --------------------------------------------------------------------

def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip)
