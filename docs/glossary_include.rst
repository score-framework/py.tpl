.. _tpl_glossary:

.. glossary::

    filter
        A feature of different :term:`template engines <template engine>` that
        works very much like a function, but has a special syntax. Jinja2, for
        example, supports such a feature_.

        .. _feature: http://jinja.pocoo.org/docs/templates/#filters

    template
        A file with replaceable parts that can be rendered with the use of
        variables to create an output in another file :term:`format
        <template format>` like HTML, XML, CSS, etc.

    template converter
        An object exposing two functions `convert_file` and `convert_string`,
        which accept the output of a file, or a file respectively. The
        conversion operation is very similar to that of a
        :term:`template engine`, but a converter does not receive any
        external variables.

        The signature of the two methods are those of the :class:`default
        converter <score.tpl.TemplateConverter>`.

        Example languages of some converters:

        - sass_
        - haml_
        - coffescript_

        .. _sass: http://sass-lang.com/
        .. _haml: http://haml.info/
        .. _coffescript: http://coffeescript.org/

    template engine
        A templating engine, which accepts a template in its own syntax and
        variables to populate the template with, and returns a processed
        string. Template engines are managed as instances of :class:`Engine
        <score.tpl.Engine>` sub-classes.
        
        Example templating engines:

        - Jinja2_
        - Mako_
        - Tenjin_
        - Chameleon_
        - Cheetah_

        .. _Jinja2: http://jinja.pocoo.org/
        .. _Mako: http://www.makotemplates.org/
        .. _Tenjin: http://www.kuwata-lab.com/tenjin/
        .. _Chameleon: http://chameleon.readthedocs.org/en/latest/
        .. _Cheetah: https://wiki.python.org/moin/Cheetah

    template format
        The file format of the template once it is rendered. This template
        property describes the language *beneath* the templating language. It
        is useful to provide different functions, filters and global variables
        for different content types.

        A template containing HTML, for example, could use a filter to escape
        javascript strings, whereas another template containing an SVG image
        would have no use for such a filter.

        Example template formats:

        - HTML
        - CSS
        - Javascript
        - SVG
        - Any other file format, really

