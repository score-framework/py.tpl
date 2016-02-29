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


class Renderer(RendererBase):

    def __init__(self, conf):
        self.conf = conf
        self._calls = []

    def add_function(self, format, name, callback, *, escape_output=True):
        self._calls.append((
            'add_function',
            [format, name, callback],
            {'escape_output': escape_output}))

    def add_filter(self, format, name, callback, *, escape_output=True):
        self._calls.append((
            'add_filter',
            [format, name, callback],
            {'escape_output': escape_output}))

    def add_global(self, format, name, value):
        self._calls.append((
            'add_global',
            [format, name, value],
            {}))

    def render_file(self, ctx, file, variables=None):
        self._flush_calls(ctx)
        exception = None
        for backend in self._backends(ctx):
            try:
                return backend.render_file(ctx, file, variables)
            except FileNotFoundError:
                pass
        raise exception

    def render_string(self, ctx, string, format, engine, variables=None):
        self._flush_calls(ctx)
        backend = next(self._backends(ctx))
        return backend.render_string(ctx, string, format, engine, variables)

    def _flush_calls(self, ctx):
        for func, args, kwargs in self._calls:
            for backend in self._backends(ctx):
                getattr(backend, func)(*args, **kwargs)
        self._calls = []

    def _backends(self, ctx):
        for alias in self.conf.backends:
            yield ctx.score._modules[alias].renderer
