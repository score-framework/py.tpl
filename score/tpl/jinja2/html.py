# Copyright © 2015-2017 STRG.AT GmbH, Vienna, Austria
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

from functools import wraps
import jinja2.ext
from score.tpl.jinja2 import GenericRenderer as RendererBase


class FilenameEmbedder(jinja2.ext.Extension):

    def preprocess(self, source, name, filename=None):
        location = name
        if filename is not None:
            location = '%s | %s' % (name, filename)
        start = '<!-- START %s -->\n\n' % location
        end = '\n\n<!-- END %s -->' % location
        source = start + source + end
        return super().preprocess(source, name, filename)


class Renderer(RendererBase):
    """
    Specific renderer for the HTML file format. The parameter *embedpaths*
    controls whether the path of each rendered template should be embedded in
    the html output.
    """

    def __init__(self, rootdir, cachedir, embedpaths):
        self.embedpaths = embedpaths
        super().__init__(rootdir, cachedir)

    def add_function(self, name, callback, escape_output=True):
        if escape_output:
            return super().add_function(name, callback)

        @wraps(callback)
        def wrapper(*args, **kwargs):
            return jinja2.Markup(callback(*args, **kwargs))
        return super().add_function(name, wrapper)

    def add_filter(self, name, callback, escape_output=True):
        if escape_output:
            return super().add_filter(name, callback)

        @wraps(callback)
        def wrapper(*args, **kwargs):
            return jinja2.Markup(callback(*args, **kwargs))
        return super().add_filter(name, wrapper)

    def build_environment(self):
        env = super().build_environment()
        env.autoescape = True
        return env

    def get_extensions(self):
        extensions = super().get_extensions()
        if self.embedpaths:
            extensions.append(FilenameEmbedder)
        return extensions
