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
[Django best practices](http://lincolnloop.com/django-best-practices/)
[Django docs 1.7](https://docs.djangoproject.com/en/1.7/)
[the right way to open sourcing a Python project](http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/) 

[静态文件哈希码以防客户端缓存过深](https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#storages)
[静态文件前缀](https://docs.djangoproject.com/en/1.6/ref/settings/#staticfiles-dirs)
[Template dir](https://docs.djangoproject.com/en/1.6/ref/settings/#template-dirs)
[Load template](https://docs.djangoproject.com/en/1.6/ref/templates/api/#loading-templates)
[Using subdirectories](https://docs.djangoproject.com/en/1.6/ref/templates/api/#using-subdirectories)
[Jinja2](https://docs.djangoproject.com/en/1.6/ref/templates/api/#using-an-alternative-template-language)
