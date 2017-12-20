.. module:: score.tpl
.. role:: confkey
.. role:: confdefault

*********
score.tpl
*********

This module handles :term:`templates <template>`, i.e. text files that
[usually] need to be pre-processed before they can be put to their actual use.
This is not just limited to typical template languages like Jinja2_ or Mako_,
but also include preprocessors for other formats like sass_ or coffescript_.

.. _Jinja2: http://jinja.pocoo.org/
.. _Mako: http://www.makotemplates.org/
.. _sass: http://sass-lang.com/
.. _coffescript: http://coffeescript.org/

Quickstart
==========

This module is usally used in combination with other modules like
:mod:`score.jinja2`, :mod:`score.css`, :mod:`score.sass`, :mod:`score.js`, etc.
So add this module and the others you need to your initialization list and
provide the root folder containing all your template files:

.. code-block:: ini

    [score.init]
    modules =
        score.tpl
        score.jinja2
        score.css

    [tpl]
    rootdir = ${here}/tpl

You can then render your templates:

>>> score.tpl.render('self-defense.jinja2', {'fruit' => 'banana'})


Configuration
=============

.. autofunction:: init


Details
=======

.. _tpl_file_types:

File Types
----------

This module primarily manages :term:`file types <file type>`: classes of files
identified by a common `mime type`_. Every file type may have an associated
list of file extensions, postprocessors and global variables.

You can define new file types accessing the :class:`FileType` objects in the
configured template module's :attr:`filetypes`:

>>> tpl.filetypes['text/plain'].extensions.append('txt')
>>> def leetify(text):
...     return text\
...             .replace('e', '3')\
...             .replace('i', '1')\
...             .replace('l', '1')\
...             .replace('t', '7')\
...             .replace('o', '0')
... 
>>> tpl.filetypes['text/plain'].postprocessors.append(leetify)

Your textual content will now always be rendered in leetspeak_.

.. _mime type: https://en.wikipedia.org/wiki/Media_type
.. _leetspeak: https://en.wikipedia.org/wiki/Leet


.. _tpl_loaders:

Loaders
-------

:class:`Loaders <Loader>` are objects that can provide the contents of
templates. They are always associated with a file extension and can be
registered with this module. The following is a loader, that can provide all
text files on your computer:

>>> tpl.loaders.append(FileSytemLoader('/', 'txt'))

If you also configure the leetify postprocessor found in the previous section,
you can read all your text files in leetspeak after finalizing the module:

>>> tpl.render('/some/text/file.txt')
'H3110 W0r1d'


.. _tpl_renderers:

Renderers
---------

It is also possible to register renderers for arbitrary file extensions. The
module will the pass the template content to the renderer for processing and
treat the return value as the new template content.

When registering renderers, they are not passed directly, but through a factory
method, which is called the :term:`engine <template engine>` in this context.
The following example creates a Renderer, that replaces all occurrences of the
string ``FRUIT`` with the *fruit* variable, that was passed to the renderer:

.. code-block:: python

    class FruitRenderer(Renderer):

        def render_string(self, string, variables, path=None):
            return string.replace('FRUIT', variables['fruit'])

    tpl.engines['txt'] = FruitRenderer

The reason for this additional layer of indirection is that some templating
engines have separate modes for different file types: The Jinja2_ renderer can
be configured to automatically escape the HTML output, for example. This means,
that the Jinja2 engine may choose to provide a different :class:`Renderer`, if
the target mime type is 'text/html'.


.. _tpl_globals:

Globals
-------

It is also possible to provide variables, that are always present in certain
file types. The following example provides the function *now* inside
'text/html' templates (for engines, that support calling functions):

>>> from datetime import datetime
>>> tpl.filetypes['text/plain'].add_global('now', datetime.now)

Your template can now always access the current time:

.. code-block:: jinja

    The current time is {{ now() }}.


.. _tpl_rendering:

Rendering Process
-----------------

When instructed to render a template, the module needs to perform these steps:

- Determine the loader to use
- Determine the file type of the template
- Determine the renderers to use

Normally, each of these decisions is trivial, but there are some cases that
need a bit more explanation. Let's look at these steps when loading the file
``myfile.css.jinja2``, a Jinja2_ file that renders content of the mime type
'text/css'.

Determining the Loader
``````````````````````

As each :class:`Loader` is associated with an extension, we will need to be
careful with file paths having more than one file extension. When loading file
``myfile.css.jinja2``, the module would first look for a Loader registered with
the extension ``css.jinja2``. If there is none, it would next look for a Loader
for ``jinja2`` files. If that doesn't exist either, the module will raise a
:class:`TemplateNotFound` exception.


Determining the File Type
`````````````````````````

A very similar process is performed for finding the file type of a template.
This time the extensions are searched backwards, though: When looking for the
file type of ``myfile.css.jinja2``, the module will first check if any file
type was registered for the extension ``css.jinja2``. If it finds none, it will
look for the mime type of the extension ``css``.


Determining Renderers
`````````````````````

When looking for the renderers to use, the module will first test if there is a
renderer for the extension ``css.jinja2``. If there is none, it will check for
two other extensions: First ``jinja2``, then ``css``. So the possible engine
list for our example path are:

- Just one engine: the one registered for the extension ``css.jinja2``
- Both ``jinja2`` and ``css`` engines.
- Just ``jinja2``
- Just ``css``


API
===

Configuration
-------------

.. autofunction:: init

.. autoclass:: ConfiguredTplModule()

    .. attribute:: filetypes

        Mapping of mime type strings to :class:`FileType` objects. Missing
        value will be created automatically, so the following code will work,
        even if no 'text/html' file type was defined yet:

        >>> tpl.filetypes['text/plain'].extensions.append('txt')

    .. attribute:: loaders

        Mapping of file extensions to :class:`Loader` instances. You can modify
        this dict to your liking until the module is :ref:`finalized
        <finalization>`.

    .. attribute:: engines

        Mapping of file extensions to callbacks capable of creating
        :class:`Engine` instances. The callback will be invoked once for every
        mime type, receiving the configured :mod:`score.tpl` module and the
        mime type to create the :class:`Renderer` for.

        Example: Assuming, that the "jinja2" engine is registered for the file
        extension "jinja2", as is the default of :mod:`score.jinja2`. When the
        :mod:`score.tpl` module is instructed to render the template
        "foo.jinja2", it will invoke the engine callback for the first time to
        create a :class:`Renderer` for the "text/html" mime type:

        >>> engine(tpl, "text/html")

        If the :mod:`score.css` module was configured, it is possible to render
        a jinja2 template to construct a css file dynamically. So if the
        :mod:`score.tpl` module is instructed to render the file called
        "bar.css.jinja2", it will invoke the engine again to obtain another
        jinja2 :class:`Renderer`:

        >>> engine(tpl, "text/css")

    .. automethod:: iter_paths

    .. automethod:: render

    .. automethod:: load

    .. automethod:: mimetype

    .. automethod:: hash

.. autoclass:: FileType()

    .. attribute:: mimetype

        The `mime type`_ associated with this file type.

    .. attribute:: extensions

        List of extensions associated with this file type. Extensions must not
        start with a period, but may contain them. Thus ``.foo`` is invalid,
        whereas ``foo`` and ``foo.bar`` are both valid.

    .. attribute:: postprocessors

        List of postprocessor callbacks for this file type. Each postprocessor
        must accept a content string (the rendered template) and return the
        modified content.

    .. attribute:: globals

        A list of :func:`namedtuples <collections.namedtuple>`, each consisting
        of the parameters passed to :meth:`add_global`.

    .. automethod:: add_global


Loader
------

.. autoclass:: Loader
    :members:

.. autoclass:: FileSystemLoader

.. autoclass:: ChainLoader


Renderer
--------

.. autoclass:: Renderer
    :members:

Exceptions
----------

.. autoclass:: TemplateNotFound

