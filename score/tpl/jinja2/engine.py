# Copyright © 2015 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

"""
Implements the :term:`engine <template engine>` for Jinja2_ templates.

.. _Jinja2: http://jinja.pocoo.org/
"""


import jinja2
from score.tpl.engine import Engine as EngineBase
from score.tpl.renderer import Renderer as RendererBase
import errno
import os


class Engine(EngineBase):
    """
    Jinja2-Specific :class:`Engine <score.tpl.Engine>`. The optional parameter
    *embedpaths* determines whether the path of each rendered HTML template
    should be embedded in an HTML comment tag in the output.
    """

    def __init__(self, embedpaths=False):
        self.embedpaths = embedpaths
        super().__init__()

    def create_subrenderer(self, format, rootdir, cachedir):
        if format == 'html':
            from .html import Renderer as HtmlRenderer
            return HtmlRenderer(rootdir, cachedir, embedpaths=self.embedpaths)
        return GenericRenderer(rootdir, cachedir)


class GenericRenderer(RendererBase):
    """
    The default :class:`Renderer <score.tpl.EngineRenderer>` of
    Jinja2-templates.
    """

    def __init__(self, rootdir, cachedir):
        self.rootdir = rootdir
        self.cachedir = cachedir
        self.globals = {}
        self.filters = {}
        self._env = None

    def add_function(self, name, value, escape_output=True):
        self.globals[name] = value
        self._env = None

    def add_filter(self, name, callback, escape_output=True):
        self.filters[name] = callback
        self._env = None

    def add_global(self, name, value):
        self.globals[name] = value
        self._env = None

    def render_string(self, ctx, string, variables=None):
        variables = self._fix_variables(ctx, variables)
        tpl = self.env.from_string(string)
        return tpl.render(variables)

    def render_file(self, ctx, filepath, variables=None):
        variables = self._fix_variables(ctx, variables)
        try:
            tpl = self.env.get_template(filepath)
            return tpl.render(variables)
        except jinja2.TemplateNotFound as e:
            if e.name == filepath:
                f = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT))
                f.filename = filepath
                raise f from e
            else:
                raise

    @property
    def env(self):
        """
        The :class:`jinja2.Environment` to use for rendering the templates.
        """
        if not self._env:
            self._env = self.build_environment()
        return self._env

    def build_environment(self):
        """
        Buids a :class:`jinja2.Environment` and registers all functions,
        filters and global variables. No need to call this function manually,
        an environment will be created automatically if it does not exist when
        accessing :attr:`.env`.
        """
        extensions = self.get_extensions()
        cache = None
        if self.cachedir:
            cache = jinja2.FileSystemBytecodeCache(self.cachedir)
        loader = jinja2.FileSystemLoader(self.rootdir)
        env = jinja2.Environment(
            autoescape=True,
            loader=loader,
            extensions=extensions,
            undefined=jinja2.StrictUndefined,
            bytecode_cache=cache,
        )
        env.globals.update(self.globals)
        env.filters.update(self.filters)
        return env

    def get_extensions(self):
        """
        The extensions to register while generating the
        :class:`jinja2.Environment` in :meth:`.build_environment`.
        """
        return ['jinja2.ext.i18n', 'jinja2.ext.autoescape']
