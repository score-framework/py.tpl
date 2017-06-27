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

"""
This module handles :term:`templates <template>`, i.e. files that need to be
pre-processed before they can be put to their actual use. The module
initialization yields a :class:`.Renderer` object, which is the central hub
for rendering templates.
"""


import os
from ._exc import TemplateNotFound
from .loader import FileSystemLoader
from collections import namedtuple, defaultdict, OrderedDict
from score.init import (
    parse_list, extract_conf, ConfiguredModule, ConfigurationError)
import re


defaults = {
    'rootdirs': [],
}


def init(confdict):
    """
    Initializes this module acoording to :ref:`our module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`rootdirs` :faint:`[default=None]`
        Denotes the root folder containing all templates. When a new format is
        created via :meth:`.Renderer.register_format`, it will have a
        sub-folder of this folder as its default root (unless, of course, the
        `rootdirs` parameter of that function is provided). If this value is
        omitted, all calls to :meth:`.Renderer.register_format` must provide a
        format-specific root folder.
    """
    conf = dict(defaults.items())
    conf['rootdirs'] = []
    conf.update(confdict)
    if 'rootdir' in conf and conf['rootdirs']:
        import score.tpl
        raise ConfigurationError(
            score.tpl, 'Both rootdir and rootdirs given')
    if 'rootdir' in conf:
        conf['rootdirs'] = conf['rootdir']
    rootdirs = parse_list(conf['rootdirs'])
    for rootdir in rootdirs:
        if not os.path.isdir(rootdir):
            import score.tpl
            raise ConfigurationError(
                score.tpl, 'Given rootdir is not a folder: %s' % (rootdir,))
    tpl = ConfiguredTplModule(rootdirs)
    extensions = set()
    for key in extract_conf(conf, 'filetype.'):
        extensions.add(key.rsplit('.', 1)[0])
    for ext in extensions:
        mimetype = conf.get('filetype.%s.mimetype' % ext)
        if mimetype is None:
            import score.tpl
            raise ConfigurationError(
                score.tpl, 'No mimetype configured for extension %s' % (ext,))
        tpl.filetypes[mimetype].extensions.append(ext)
    return tpl


class ConfiguredTplModule(ConfiguredModule):
    """
    This module's :class:`configuration class
    <score.init.ConfiguredModule>`.
    """

    def __init__(self, rootdirs):
        super().__init__(__package__)
        self.rootdirs = rootdirs
        self.filetypes = FileTypes(self)
        self.loaders = Loaders(self)
        self.engines = Engines(self)
        self._renderers = defaultdict(dict)

    def define_global(self, mimetype, name, value, escape=True):
        self.filetypes[mimetype].add_global(name, value, escape=escape)

    def iter_paths(self, mimetype=None):
        def all_paths():
            for mimetype in self.filetypes:
                for extension in self.filetypes[mimetype].extensions:
                    for loader in self.loaders[extension]:
                        yield from loader.iter_paths()

        def valid_paths():
            for path in all_paths():
                try:
                    self._find_filetype(path)
                    yield path
                except TemplateNotFound:
                    pass

        if mimetype:
            extensions = self.filetypes[mimetype].extensions
            regex = re.compile(r'(^|/)[^/.]+\.(%s)($|\.)' %
                               '|'.join(map(re.escape, extensions)))
            for path in valid_paths():
                if regex.search(path):
                    yield path
        else:
            yield from valid_paths()

    def load(self, path):
        return self._find_loader(path).load(path)

    def render(self, path, variables=None, *, apply_postprocessors=True):
        filetype = self._find_filetype(path)
        is_file, result = self.load(path)
        if variables is None:
            variables = {}
        for renderer in self._find_renderers(path, filetype=filetype):
            if is_file:
                result = renderer.render_file(result, variables, path=path)
                is_file = False
            else:
                result = renderer.render_string(result, variables, path=path)
        if is_file:
            result = open(result).read()
        if apply_postprocessors:
            for postprocessor in filetype.postprocessors:
                result = postprocessor(result)
        return result

    def mimetype(self, path):
        return self._find_filetype(path).mimetype

    def hash(self, path):
        return self._find_loader(path).hash(path)

    def _finalize(self):
        # make sure that every file extension is associated with
        # at most one filetype
        all_extensions = set()
        for filetype in self.filetypes.values():
            duplicates = all_extensions.intersection(filetype.extensions)
            if not duplicates:
                all_extensions |= set(filetype.extensions)
                continue
            extension = duplicates.pop()
            filetypes = [f for f in self.filetypes
                         if extension in f.extensions.extensions]
            import score.tpl
            raise ConfigurationError(
                score.tpl,
                'Extension %s registered with multiple mimetypes: %s' %
                (extension, filetypes))
        for extension in self.loaders:
            if extension not in all_extensions:
                import score.tpl
                raise ConfigurationError(
                    score.tpl,
                    'Loader Extension "%s" has no filetype' % (extension,))
        for extension in self.engines:
            if extension not in all_extensions:
                import score.tpl
                raise ConfigurationError(
                    score.tpl,
                    'Engine Extension "%s" has no filetype' % (extension,))
        # sort loaders and engines by length of extension string
        # this is important, as we want to test 'tar.gz' before 'gz'
        self.loaders = OrderedDict(
            (ext, self.loaders[ext])
            for ext in sorted(all_extensions, key=len, reverse=True))
        self.engines = OrderedDict(
            (ext, self.engines[ext])
            for ext in sorted(self.engines, key=len, reverse=True))

    def _find_loader(self, path):
        parts = os.path.basename(path).split('.', maxsplit=1)
        if len(parts) == 1:
            # TODO: other exception?
            raise TemplateNotFound(path)
        if parts[1] not in self.loaders:
            while '.' in parts[1]:
                more_parts = parts[1].split('.', maxsplit=1)
                parts[0] += '.' + more_parts[0]
                parts[1] = more_parts[1]
                if parts[1] in self.loaders:
                    break
            else:
                raise TemplateNotFound(path)
        for loader in self.loaders[parts[1]]:
            if loader.is_valid(path):
                return loader
        raise TemplateNotFound(path)

    def _find_renderers(self, path, *, filetype=None):
        renderers = []
        filename = os.path.basename(path)
        if filetype is None:
            filetype = self._find_filetype(path)
        while True:
            candidates = []
            for extension, engine in self.engines.items():
                idx = filename.rfind('.%s' % extension)
                if idx < 0:
                    continue
                candidates.append((extension, idx, engine))
            if not candidates:
                break
            extension, idx, engine = sorted(
                candidates, key=lambda x: (x[1] + len(x[0]), len(x[0])),
                reverse=True)[0]
            filename = filename[:len(extension) + 1]
            if filetype not in self._renderers[engine]:
                self._renderers[engine][filetype] = engine(self, filetype)
            renderers.append(self._renderers[engine][filetype])
        return renderers

    def _find_filetype(self, path):
        filename = os.path.basename(path)
        extensions = filename.split('.')[1:]
        for i in range(len(extensions), 0, -1):
            extension = '.'.join(extensions[:i])
            try:
                return next(f for f in self.filetypes.values()
                            if extension in f.extensions)
            except StopIteration:
                pass
        raise TemplateNotFound(path)


class Loaders(defaultdict):

    def __init__(self, conf):
        self.conf = conf
        super().__init__()

    def __missing__(self, key):
        if '/' in key:
            raise ValueError('Invalid File extension "%s"' % (key,))
        loaders = list()
        if self.conf.rootdirs:
            loaders.append(FileSystemLoader(self.conf.rootdirs, key))
        self[key] = loaders
        return loaders


class Engines(dict):

    def __init__(self, conf):
        self.conf = conf
        super().__init__()

    def __setitem__(self, key, value):
        if key in self:
            raise ValueError(
                'Renderer for extension `%s` already defined as %s' %
                (key, repr(self[key])))
        if '/' in key:
            raise ValueError('Invalid File extension "%s"' % (key,))
        return super().__setitem__(key, value)


class FileTypes(defaultdict):

    def __init__(self, conf):
        self.conf = conf
        super().__init__()

    def __missing__(self, key):
        filetype = FileType(self.conf, key)
        self[key] = filetype
        return filetype


class FileType:

    def __init__(self, conf, mimetype):
        self.__conf = conf
        self.__mimetype = mimetype
        self.__extensions = []
        self.__postprocessors = []
        self.__globals = []
        self.__finalized = False
        self.__escape = None

    def _finalize(self):
        # TODO: check for duplicates in extensions
        self.__extensions = tuple(self.__extensions)
        self.__postprocessors = tuple(self.__postprocessors)
        self.__globals = tuple(self.__globals)
        self.__finalized = True

    @property
    def mimetype(self):
        return self.__mimetype

    @property
    def extensions(self):
        return self.__extensions

    @extensions.setter
    def extensions(self, value):
        assert not self.__finalized
        self.__extensions = value

    @property
    def postprocessors(self):
        return self.__postprocessors

    @postprocessors.setter
    def postprocessors(self, value):
        assert not self.__finalized
        self.__postprocessors = value

    @property
    def escape(self):
        return self.__escape

    @escape.setter
    def escape(self, callback):
        assert not self.__finalized
        self.__escape = callback

    @property
    def globals(self):
        return self.__globals

    def add_global(self, name, value, *, escape=True):
        assert not self.__finalized
        assert not any(x for x in self.__globals if x.name == name)
        self.__globals.append(VariableDefinition(name, value, escape))


VariableDefinition = namedtuple('VariableDefinition',
                                ('name', 'value', 'escape'))
