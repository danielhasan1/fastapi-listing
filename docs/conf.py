# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# try:
#     from importlib.metadata import version as get_version
# except ImportError: # for Python<3.8
#     from importlib_metadata import version as get_version

# from packaging.version import parse
# v = parse(get_version("fastapi_listing"))
import os


def get_version():
    package_init = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "fastapi_listing", "__init__.py"
    )
    with open(package_init) as f:
        for line in f:
            if line.startswith("__version__ ="):
                return line.split("=")[1].strip().strip("\"'")


project = 'fastapi-listing'
copyright = '2023, Danish Hasan'
author = 'Danish Hasan'
# version = v.base_version
# release = v.public
version = get_version()
release = get_version()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
    "sphinx.ext.autosectionlabel",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
autodoc_default_options = {"members": True, "show-inheritance": True}
# pygments_style = "sphinx"
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}
htmlhelp_basename = "fastapilistingdoc"
todo_include_todos = False
