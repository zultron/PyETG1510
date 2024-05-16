# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from enum import Enum

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------

project = "PyETG1510"
titles = ["ETG. 1510", "EtherCAT main device diagnosis interface client library", "for Python"]
copyright = "2023, Beckhoff Automation K.K."
author = "Takashi Ichihashi"
autodoc_mock_imports = ["bitarray"]

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "japanesesupport",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


myst_enable_extensions = [
    "amsmath",
    "attrs_image",
    "colon_fence",
    "deflist",
    "dollarmath",
    "amsmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    # "inv_link",
    # "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

numfig = True

suppress_warnings = ["myst.header"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for apidoc -------------------------------------------------

autodoc_default_options = {"special-members": "__init__", "undoc-members": False, "exclude-members": "__init__"}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for LaTeX output -------------------------------------------------


latex_elements = {
    # Latex figure (float) alignment
    #
    "figure_align": "H",
    "sphinxsetup": "verbatimforcewraps, verbatimmaxunderfull=0",
}


latex_engine = "lualatex"

latex_docclass = {"manual": "ltjsbook"}

# Concatenate with line break command `\\` in between
my_latex_title_lines = "\\\\".join(titles)


class Author(Enum):
    organization: str = "Beckhoff Automation Co., Ltd."
    author_native: str = "市橋 卓"
    author_en: str = "Takashi Ichihashi"

    @classmethod
    def get_strings(cls, delimiter=" "):
        return delimiter.join([e.value for e in cls])


latex_elements = {
    # (C) Polyglossia Prevent loading packages
    "polyglossia": "",
    "fontpkg": r"""
        \setmainfont{DejaVu Serif}
        \setsansfont{DejaVu Sans}
        \setmonofont{DejaVu Sans Mono}
        """,
    "preamble": r"""

        % Bringing my_latex_title_lines into the LaTeX world
        \newcommand{\mylatextitlelines}{"""
    + my_latex_title_lines
    + r"""}
        \newcommand{\mylatexauthorlines}{"""
    + Author.get_strings("\\\\")
    + r"""}

        % Since the at sign is used in the cover template, treat it as a normal character.
        \makeatletter

        % Redefine cover template(B)
        \renewcommand{\sphinxmaketitle}{%
            \let\sphinxrestorepageanchorsetting\relax
            \ifHy@pageanchor\def\sphinxrestorepageanchorsetting{\Hy@pageanchortrue}\fi
            \hypersetup{pageanchor=false}% avoid duplicate destination warnings
            \begin{titlepage}%
                \let\footnotesize\small
                \let\footnoterule\relax
                \noindent\rule{\textwidth}{1pt}\par
                \begingroup % for PDF information dictionary
                \def\endgraf{ }\def\and{\& }%
                \pdfstringdefDisableCommands{\def\\{, }}% overwrite hyperref setup
                \hypersetup{pdfauthor={\@author}, pdftitle={\@title}}%
                \endgroup
                \begin{flushright}%
                \sphinxlogo
                \py@HeaderFamily
                {\Huge \mylatextitlelines \par} % <--- ここで\mylatextitlelinesを使用(C)
                {\itshape\LARGE \py@release\releaseinfo \par}
                \vfill
                {\LARGE
                    \begin{tabular}[t]{l}
                    \mylatexauthorlines
                    %\@author
                    \end{tabular}\kern-\tabcolsep
                    \par}
                \vfill\vfill
                {\large
                \@date \par
                \vfill
                \py@authoraddress \par
                }%
                \end{flushright}%\par
                \@thanks
            \end{titlepage}%
            \setcounter{footnote}{0}%
            \let\thanks\relax\let\maketitle\relax
            %\gdef\@thanks{}\gdef\@author{}\gdef\@title{}
            \clearpage
            \ifdefined\sphinxbackoftitlepage\sphinxbackoftitlepage\fi
            \if@openright\cleardoublepage\else\clearpage\fi
            \sphinxrestorepageanchorsetting
        } % cover style end
        % Change the at sign back to a special character
        \makeatother

        \setcounter{tocdepth}{1}
        \usepackage[titles]{tocloft}
        %\usepackage[OT1]{fontenc}
        \cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
        \setlength{\cftchapnumwidth}{1.5cm}
        \setlength{\cftsecindent}{\cftchapnumwidth}
        \setlength{\cftsecnumwidth}{1.25cm}
        \addtolength{\footskip}{0mm}
        """,
    "fncychap": r"\usepackage[Bjornstrup]{fncychap}",
    "printindex": r"\footnotesize\raggedright\printindex",
}


latex_show_urls = "footnote"
