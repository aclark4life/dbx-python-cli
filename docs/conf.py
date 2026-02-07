"""Sphinx configuration for dbx-python-cli documentation."""

import os
import sys

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath("../src"))

# Project information
project = "dbx-python-cli"
copyright = "2024, MongoDB DBX Python"
author = "MongoDB DBX Python"
release = "0.1.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output options
html_theme = "furo"
html_title = "dbx-python-cli"
html_static_path = ["_static"]

# Furo theme options
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

# Sidebar depth
html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}

# Set the depth of the table of contents in the sidebar
toctree_collapse = False

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
