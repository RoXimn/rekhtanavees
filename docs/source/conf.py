# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2024. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
# ******************************************************************************

project = 'Rekhta Navees'
copyright = '2025, RoXimn'
author = 'RoXimn'
release: str = '0.1.0a'
master_doc: str = 'index'
language: str = 'en-US'
modindex_common_prefix: list[str] = ['R', 'rekhtanavees']

# autodoc_mock_imports = ['settings']

# -- General configuration ---------------------------------------------------
extensions: list[str] = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
    'sphinxcontrib.autodoc_pydantic',
]
napoleon_google_docstring = True

source_suffix: str = '.rst'
todo_include_todos: bool = True

templates_path = ['_templates']
exclude_patterns = []

# Pydantic autodoc settings ----------------------------------------------------
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_config_members = False
autodoc_pydantic_settings_signature_prefix = 'Settings'
autodoc_pydantic_model_signature_prefix = 'Schema'
autodoc_pydantic_model_member_order = 'alphabetical'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_book_theme'
html_theme_options = {
    'navigation_with_keys': False,
    "repository_url": "https://github.com/RoXimn/rekhtanavees",
    "use_repository_button": True,
}

html_logo = "_static/feather.png"
html_title = "Rekhta Navees"

html_static_path = ['_static']
html_css_files = [
    'custom.css',
]
html_show_sourcelink = False
