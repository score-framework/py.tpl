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
This package :ref:`integrates <framework_integration>` the module with
pyramid.
"""
import score.tpl
import pyramid.threadlocal


def init(confdict, configurator, webassets_conf=None):
    """
    This will call the generic initializer and wrap the resulting renderer
    in this package's :class:`.PyramidRenderer`, which registers all engines
    with :term:`pyramid's rendering system <pyramid:renderer>`.
    """
    tplconf = score.tpl.init(confdict, webassets_conf)
    tplconf.renderer = PyramidRenderer(configurator, tplconf.renderer)
    return tplconf


class PyramidRenderer(score.tpl.Renderer):
    """
    A sub-class of the more generic :class:`Renderer <score.tpl.Renderer>`
    which registers all possible extensions with
    :term:`pyramid's rendering system <pyramid:renderer>`.
    """

    def __init__(self, configurator, renderer):
        self.configurator = configurator
        self.renderer = renderer
        for engine in self.renderer.engines:
            self._register_pyramid_renderer(engine)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.renderer, attr)

    def register_engine(self, extension, engine):
        self.renderer.register_engine(extension, engine)
        self._register_pyramid_renderer(extension)
        for format_ in self.formats:
            self._register_pyramid_renderer('%s.%s' % (format_, extension))

    def register_format(self, name, rootdir=None, cachedir=None,
                        converter=None):
        self.renderer.register_format(name, rootdir, cachedir, converter)
        self._register_pyramid_renderer(name)
        for extension in self.engines:
            self._register_pyramid_renderer('%s.%s' % (name, extension))

    def render_file(self, file, variables=None):
        variables = self._mkvariables(variables)
        return super().render_file(file, variables)

    def render_string(self, string, format, engine, variables=None):
        variables = self._mkvariables(variables)
        return super().render_string(string, format, engine, variables)

    def _mkvariables(self, variables):
        if variables is None:
            variables = {}
        if 'request' not in variables:
            request = pyramid.threadlocal.get_current_request()
            if request is not None:
                variables['request'] = request
        return variables

    def _register_pyramid_renderer(self, ext):
        def renderer(info):
            def render(value, system):
                if 'request' not in value and system['request'] is not None:
                    value['request'] = system['request']
                return self.render_file(info.name, value)
            return render
        self.configurator.add_renderer('.%s' % ext, renderer)
