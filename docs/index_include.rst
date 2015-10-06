.. module:: score.tpl
.. role:: faint
.. role:: confkey

*********
score.tpl
*********

Introduction
============

This module handles :term:`templates <template>`, i.e. files that need to be
pre-processed before they can be put to their actual use. The central class
for converting templates to their target format is the
:class:`score.tpl.Renderer`.

.. _tpl_templates:

Templates
---------

Every template has a target :term:`format <template format>`, i.e. the file
format of the rendered template. This could be an arbitrary file format, like
HTML, CSS, Javascript, SVG or even binary formats like ZIP or PNG.

:term:`Template formats <template format>` must be defined explicitly during
the initialization of an application. After a format was registered in the
configured :class:`renderer <score.tpl.Renderer>`, additional resources may
be registered for that template format. These resources are:

- functions,
- filters and
- global values.

These resources are available globally in the templates of that format.

.. _tpl_functions:

Functions
`````````

A registered function usually generates an output that is to be embedded in
the rendered template. How the function needs to be called is left to the
engine rendering the template, but it *must* provide all registered functions
within templates.

A web application hosting articles, where the background color for each
article can be set by the editor creating the article, might have a global
function ``article_css``, which accepts an article object and generates the
necessary style sheets for that article.

Such a function might be useful in templates rendering CSS files, as well as
those rendering HTML (for embedding inline styles in certain cases).

.. _tpl_filters:

Filters
```````

A filter is very much like a function, but accepts just a single value and
returns another value. Some engines have a special syntax for filters allowing
a very readable use of these functions.

An application using big numbers might want to convert them to a more
human-readable string using a certain locale. If one would, for example,
register a filter called ``gernum``, which converts numbers to strings in
the german locale, the following Jinja2_ template::

    {{ 123456789.01 | gernum }}

… would render as::

    123.456.789,01

.. _tpl_globals:

Global Variables
````````````````

It is also possible to register other global values that are present in *all*
templates of given format.

.. todo::
    Does this need more documentation?

.. _tpl_engines:

Engines
-------

The conversion to the target *format* is performed by an :term:`engine
<template engine>`. An engine receives a template (either as a string or a
file name) and returns the rendered template in its target *format* as a
string.

An example engine is Jinja2_. It can convert the following template string::

    <html>
        <body>
            Hello, {{ user.fullname }}!
        </body>
    </html>

to the following HTML::

    <html>
        <body>
            Hello, Sir Robin the Not-Quite-So-Brave-As-Sir-Lancelot!
        </body>
    </html>

As we can see in the example, it requires a ``user`` object to do so. This
``user`` value must be provided for the rendering to succeed.

.. _Jinja2: http://jinja.pocoo.org/

.. _tpl_converters:

Converters
----------

:term:`Template formats <template format>` may also have a
:class:`converter object <score.tpl.TemplateConverter>`, which further
transforms the output of an engine.

An example might be an HTML minifier, which converts the example output of the
above template into the following string::

    <html><body>Hello, Sir Robin the Not-Quite-So-Brave-As-Sir-Lancelot!</body></html>

The difference between a *converter* and an *engine* is that a *converter*
does not receive any variables. Nor does it receive any of the functions,
filters or global variables of its file format. It must operate with whatever
resources it had at the time the *converter* was registered - usually during
the initialization of the application.

.. _tpl_rendering:

Rendering Process
-----------------

When instructed to render a template in a given :term:`template format` with a
given :term:`template engine`, the :class:`Renderer <score.tpl.Renderer>` will
first call the *template engine*. That call will execute and result in a
string in the template's file *format*.

If that registered *template format* has a configured
:term:`template converter`, the string produced in the previous step will be
passed to that *converter* function to yield a new string.

The resulting string is the return value of the rendering process.

If no :term:`template engine` was given, the file is just processed by the
*converter*, which directly generates the output of the rendering process.

The whole process as a graph::

    .                       +---------------+
                            | Invoke engine |
                            +---------------+
                             ^            |
                             | yes        |
                             |            V
               +--------------+    no    +------------------+
    *path* --> | Have engine? | -------->| Invoke converter | --> output
               +--------------+          +------------------+


The :class:`Renderer <score.tpl.Renderer>` in this module will try to
determine the :term:`template format` and the :term:`template engine` to use
with the help of a file's extensions.

It assumes that the name of a file format is also the extension for files of
that type. If the file format is ``css``, for example, it assumes that all
files with that extension have that format.

All files may have an optional *engine extension*, as well. If ``jinja2`` and
``mako`` are registered *engine extensions*, the following paths will all be
detected as ``css`` files:

- ``reset.css``
- ``reset.css.jinja2``
- ``reset.css.mako``

Furthermore, if ``css`` was configured to be the default template format, the
following files will also be treated as ``css`` files:

- ``reset`` (no engine)
- ``reset.js`` (no engine)
- ``reset.txt`` (no engine)
- ``reset.jinja2`` (engine = jinja2)
- ``reset.mako`` (engine = mako)

Configuration
=============

.. autofunction:: score.tpl.init

.. autoclass:: score.tpl.ConfiguredTplModule()

    .. attribute:: renderer

        The :class:`template renderer <score.tpl.Renderer>` for this
        configuration. Other modules might register functions, filters and
        globals to this object.

    .. attribute:: rootdir

        The *root* folder of all templates. This value is either `None` -
        meaning that no root folder was configured, or it points to an
        existing folder on the file system.

    .. attribute:: cachedir

        Cache folder for all templates. This value is either `None` or it
        points to an existing and writable folder on the file system.

    .. attribute:: default_format

        The :term:`file format <template format>` to assume if it cannot be
        determined automatically. Might be `None`.

Renderer
========

.. autoclass:: score.tpl.Renderer
    :members:

Converter
=========

.. autoclass:: score.tpl.TemplateConverter
    :members:

Engine
======

.. autoclass:: score.tpl.Engine
    :members:

.. autoclass:: score.tpl.EngineRenderer
    :members:

jinja2
------

.. note::
    Currently, Jinja2_ is the only engine this module supports.

    .. _Jinja2: http://jinja.pocoo.org/

.. automodule:: score.tpl.jinja2

.. autoclass:: score.tpl.jinja2.Engine
    :members:

.. autoclass:: score.tpl.jinja2.GenericRenderer
    :members:

.. autoclass:: score.tpl.jinja2.html.Renderer
    :members:


Pyramid Integration
===================

.. automodule:: score.tpl.pyramid
    :members:

