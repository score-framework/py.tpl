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

import logging
from .renderer import Renderer as RendererBase
from score.init import parse_list, ConfiguredModule
from collections import OrderedDict


log = logging.getLogger('score.tpl.fallback')
defaults = {
    'backends': []
}


def init(confdict, webassets=None):
    """
    Initializes this module acoording to :ref:`our module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`backends`
        List of score module aliases that should be used as backends to the
        templating.
    """
    conf = dict(defaults.items())
    conf.update(confdict)
    backends = parse_list(conf['backends'])
    assert backends, 'No backends configured'
    return ConfiguredTplFallbackModule(backends)


class ConfiguredTplFallbackModule(ConfiguredModule):
    """
    This module's :class:`configuration class
    <score.init.ConfiguredModule>`.
    """

    def __init__(self, backends):
        super().__init__(__package__)
        self.backends = backends
        self.renderer = Renderer(self)
        self._finalize_dependencies = backends

    def _finalize(self, **kwargs):
        self.renderer._set_backends(kwargs)


class Renderer(RendererBase):

    def __init__(self, conf):
        self.conf = conf
        self._calls = []

    @property
    def formats(self):
        return [format
                for backend in self._backends.values()
                for format in backend.formats]

    def add_function(self, format, name, callback, *, escape_output=True):
        if hasattr(self, '_backends'):
            for backend in self._backends.values():
                backend.renderer.add_function(format, name, callback,
                                              escape_output=escape_output)
        else:
            self._calls.append((
                'add_function',
                [format, name, callback],
                {'escape_output': escape_output}))

    def add_filter(self, format, name, callback, *, escape_output=True):
        if hasattr(self, '_backends'):
            for backend in self._backends.values():
                backend.renderer.add_filter(format, name, callback,
                                            escape_output=escape_output)
        else:
            self._calls.append((
                'add_filter',
                [format, name, callback],
                {'escape_output': escape_output}))

    def add_global(self, format, name, value):
        if hasattr(self, '_backends'):
            for backend in self._backends.values():
                backend.renderer.add_global(format, name, value)
        else:
            self._calls.append((
                'add_global',
                [format, name, value],
                {}))

    def render_file(self, ctx, file, variables=None):
        for backend in self._backends.values():
            try:
                return backend.renderer.render_file(ctx, file, variables)
            except FileNotFoundError as e:
                if e.filename != file:
                    raise
        raise FileNotFoundError(file)

    def render_string(self, ctx, string, format, engine, variables=None):
        backend = next(self._backends.values())
        return backend.renderer.render_string(
            ctx, string, format, engine, variables)

    def _set_backends(self, backends):
        self._backends = OrderedDict()
        for backend in self.conf.backends:
            self._backends[backend] = backends[backend]
        for func, args, kwargs in self._calls:
            for backend in self._backends.values():
                getattr(backend.renderer, func)(*args, **kwargs)
        self._calls = []
