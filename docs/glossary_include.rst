.. _tpl_glossary:

.. glossary::

    template
        A text file that needs to be pre-processed before it can be put to its
        intended use. This includes template languages like Jinja2_ or Mako_,
        as well as preprocessors for other formats like sass_ or coffescript_.

        .. _Jinja2: http://jinja.pocoo.org/
        .. _Mako: http://www.makotemplates.org/
        .. _sass: http://sass-lang.com/
        .. _coffescript: http://coffeescript.org/

    template engine
        A callback function, that will construct :class:`score.tpl.Renderer`
        instances. See :attr:`score.tpl.ConfiguredTplModule.engines` for a
        more detailed explanation.
