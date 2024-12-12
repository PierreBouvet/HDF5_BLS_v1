import os
import sys
sys.path.insert(0, os.path.abspath('../my_project'))

project = 'My Project'
author = 'Your Name'
release = '0.1.0'

extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'alabaster'