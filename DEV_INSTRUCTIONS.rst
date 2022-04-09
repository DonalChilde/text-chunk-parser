================
Dev Instructions
================

Initial Project Setup
---------------------

From the project directory, run

.. code-block:: bash

    # Make a virtualenv in the project directory, and install requirements.
    ./scripts/run.sh venv:init:all
    # Activate the virtualenv
    source ./.venv/bin/activate
    # Make a local git repo
    ./scripts/run.sh git:init
    # Initial commit. Repeat both commands if git hooks modify files.
    git add .
    git commit -m "initial commit"
    # To set a github remote origin...
    # https://docs.github.com/en/github/using-git/adding-a-remote
    git remote add origin https://github.com/DonalChilde/text_chunk_parser.git
    # install an editable link to source
    pip install -e .
    # check that the tests pass
    pytest
    # generate the docs
    ./scripts/run.sh docs:build


Downloading project from github
-------------------------------

From the parent directory of the project

.. code-block:: bash

    git clone git@github.com:DonalChilde/text_chunk_parser.git


TODO project setup from github

Remove Example Code
-------------------

TODO List code modules and doc files to be removed.


Tips and fixes
--------------


Git
^^^
To run git commit without git precommit hooks -

.. code-block:: bash

    git commit -m "Some comments" --no-verify

Docs
^^^^
Generate docs with:
.. code-block:: bash

    ./scripts/run.sh docs:build

Normally, there are no `heading levels`_ assigned to certain characters as the structure is determined from the succession of headings. However, it is better to stick to the same convention throughout a project. For instance:

.. _`heading levels`: https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html#headings

   * # with overline, for parts
   * \* with overline, for chapters
   * =, for sections
   * -, for subsections
   * ^, for subsubsections
   * “, for paragraphs
