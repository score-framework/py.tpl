# Copyright © 2015,2016 STRG.AT GmbH, Vienna, Austria
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
This module handles :term:`templates <template>`, i.e. files that need to be
pre-processed before they can be put to their actual use. The module
initialization yields a :class:`.Renderer` object, which is the central hub
for rendering templates.
"""


import os
from ._exc import TemplateNotFound
from .loader import FileSystemLoader
from collections import nametuple, defaultdict
from score.init import (
    init_cache_folder, ConfiguredModule, ConfigurationError
)


defaults = {
    'rootdirs': [],
    'cachedir': None,
}


def init(confdict, webassets=None):
    """
    Initializes this module acoording to :ref:`our module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`rootdirs` :faint:`[default=None]`
        Denotes the root folder containing all templates. When a new format is
        created via :meth:`.Renderer.register_format`, it will have a
        sub-folder of this folder as its default root (unless, of course, the
        `rootdir` parameter of that function is provided). If this value is
        omitted, all calls to :meth:`.Renderer.register_format` must provide a
        format-specific root folder.

    :confkey:`cachedir` :faint:`[default=None]`
        A cache folder that will be used to cache rendered templates. Will
        fall back to a sub-folder (called ``tpl``) of the cachedir in the
        *webassets*, if one was provided.

        Although this module will work without a cache folder, it is highly
        recommended that it is either initialized with a ``cachedir`` or a
        *webassets* with a valid ``cachedir``, even if the value points
        to the system's temporary folder.
    """
    conf = dict(defaults.items())
    conf['rootdirs'] = list(conf['rootdirs'])
    conf.update(confdict)
    if not conf['cachedir'] and webassets and webassets.cachedir:
        conf['cachedir'] = os.path.join(webassets.cachedir, 'tpl')
    if conf['cachedir']:
        init_cache_folder(conf, 'cachedir', autopurge=True)
    if conf['rootdir']:
        conf['rootdirs'].append(conf['rootdir'])
    for rootdir in conf['rootdirs']:
        if not os.path.isdir(rootdir):
            import score.tpl
            raise ConfigurationError(
                score.tpl, 'Given rootdir is not a folder: %s' % (rootdir,))
    return ConfiguredTplModule(conf['cachedir'], conf['rootdirs'])


class ConfiguredTplModule(ConfiguredModule):
    """
    This module's :class:`configuration class
    <score.init.ConfiguredModule>`.
    """

    def __init__(self, rootdirs, cachedir, default_format):
        super().__init__(__package__)
        self.rootdirs = rootdirs
        self.cachedir = cachedir
        self.default_format = default_format
        self.filetypes = {}
        self.globals = defaultdict(list)

    def define_filetype(self, extension, engine_factories, mimetype,
                        extra_loaders=None):
        if extension[0] != '.':
            extension = '.%s' % (extension,)
        assert not self._finalized
        assert extension not in self.filetypes
        if not extra_loaders and not self.rootdirs:
            raise Exception('No rootdirs, no loader')  # TODO!!
        engines = []
        for Engine in engine_factories:
            engine = Engine(self, extension, mimetype)
            for var in self.globals[mimetype]:
                engine.add_global(var.name, var.value, var.needs_escaping)
            engines.append(engine)
        loaders = [FileSystemLoader(self.rootdirs, extension)] + extra_loaders
        self.filetypes[extension] = FileType(
            extension, engines, mimetype, loaders)

    def define_global(self, mimetype, name, value, needs_escaping=True):
        assert not self._finalized
        assert not any(x for x in self.globals[mimetype] if x.name == name)
        self.globals[mimetype].append(
            VariableDefinition(name, value, needs_escaping))
        for filetype in self.filetypes.values():
            if mimetype and filetype.mimetype != mimetype:
                continue
            for engine in filetype.engines:
                engine.add_global(name, value, needs_escaping)

    def iter_paths(self, mimetype=None):
        for filetype in self.filetypes.values():
            if mimetype and filetype.mimetype != mimetype:
                continue
            yield from filetype.loader.iter_paths()

    def render(self, path, variables):
        parts = os.path.basename(path).split('.', maxsplit=1)
        if len(parts) == 1:
            # TODO: other exception?
            raise TemplateNotFound(path)
        if parts[1] not in self.filetypes:
            raise TemplateNotFound(path)
        filetype = self.filetypes[parts[1]]
        is_file, result = filetype.loader.load(path)
        for engine in filetype.engines:
            if is_file:
                result = engine.render_file(result, variables, path=path)
                is_file = False
            else:
                result = engine.render_string(result, variables, path=path)
        if is_file:
            result = open(result).read()
        return result

    def hash(self, path):
        parts = os.path.basename(path).split('.', maxsplit=1)
        if len(parts) == 1:
            # TODO: other exception?
            raise TemplateNotFound(path)
        if parts[1] not in self.filetypes:
            raise TemplateNotFound(path)
        filetype = self.filetypes[parts[1]]
        return filetype.loader.hash(path)


FileType = nametuple('FileType',
                     ('extension', 'engines', 'mimetypes', 'loader'))


VariableDefinition = nametuple('VariableDefinition',
                               ('name', 'value', 'needs_escaping'))
