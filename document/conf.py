"""项目文档."""
import os
import sys
import json
import datetime
from pathlib import Path
import recommonmark
from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser
project_home = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(project_home))

with open(project_home.joinpath("pmfprc.json")) as project_info_json:
    project_info = json.load(project_info_json)

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.extlinks'
]

templates_path = ['_templates']

source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}
source_suffix = ['.rst', '.md']
master_doc = 'index'
project = project_info["project-name"]
year = datetime.datetime.now().year
author = project_info["author"]
copyright = f'{year}, {author}'
version = project_info["version"]
release = ''
language = 'zh'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = True
html_theme = 'alabaster'
#html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
htmlhelp_basename = project_info["project-name"]
latex_elements = {
}
latex_documents = [
    (
        master_doc,
        f'{project}.tex',
        f'{project} Documentation',
        'Author',
        'manual'
    ),
]

man_pages = [
    (
        master_doc,
        project,
        f'{project} Documentation',
        [author],
        1)
]

texinfo_documents = [
    (master_doc, project, f'project Documentation',
     author, project, 'One line description of project.',
     'Miscellaneous'),
]

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ['search.html']
todo_include_todos = True
url_doc_root = project_info["url"]

html_theme_options = {
    'description': 'Tools for develope asynchronous script easily.',
    'github_user': "Python-Tools",
    'github_repo': 'aio_parallel_tools',
    'github_banner': True,
    'github_button': True,
    'sidebar_collapse': False
}

locale_dirs = ['locale/']
gettext_compact = False
extlinks = {
    "locale":(f"{url_doc_root}%s/index.html","")
}

def setup(app):
    app.add_config_value('recommonmark_config', {
        'url_resolver': lambda url: url_doc_root + url,
        'auto_toc_tree_section': 'Contents',
        'enable_math': True,
        'enable_inline_math': True
    }, True)
    app.add_transform(AutoStructify)
