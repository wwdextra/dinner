.. 

Dinner
======================

Quickstart
----------

To bootstrap the project::

    virtualenv src
    source src/bin/activate
    cd path/to/src/repository
    pip install -r requirements.pip
    pip install -e .
    cp src/settings/local.py.example src/settings/local.py
    manage.py syncdb --migrate

Documentation
-------------

Developer documentation is available in Sphinx format in the docs directory.

Initial installation instructions (including how to build the documentation as
HTML) can be found in docs/install.rst.

Refference
-------------
[Django layout](https://github.com/micfan/django-layout)
