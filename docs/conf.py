import os
import sys

import oltl

sys.path.insert(0, os.path.abspath("../"))

project = oltl.__name__
author = "osoken"

version = oltl.__version__
release = oltl.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

language = "en"
