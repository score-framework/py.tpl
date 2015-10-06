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
This module handles :term:`templates <template>`, i.e. files that need to be
pre-processed before they can be put to their actual use. The module
initialization yields a :class:`.Renderer` object, which is the central hub
for rendering templates.
"""


from abc import ABCMeta, abstractmethod
import logging
import os
from score.init import (
    extract_conf, init_cache_folder,
    init_object, ConfiguredModule
)


log = logging.getLogger(__name__)
defaults = {
    'rootdir': None,
    'cachedir': None,
    'default_format': None,
}


def init(confdict, webassets_conf=None):
    """
    Initializes this module acoording to :ref:`our module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`rootdir` :faint:`[default=None]`
        Denotes the root folder containing all templates. When a new format is
        created via :meth:`.Renderer.register_format`, it will have a
        sub-folder of this folder as its default root (unless, of course, the
        `rootdir` parameter of that function is provided). If this value is
        omitted, all calls to :meth:`.Renderer.register_format` must provide a
        format-specific root folder.

    :confkey:`cachedir` :faint:`[default=None]`
        A cache folder that will be used to cache rendered templates. Will
        fall back to a sub-folder (called ``tpl``) of the cachedir in the
        *webassets_conf*, if one was provided.

        Although this module will work without a cache folder, it is highly
        recommended that it is either initialized with a ``cachedir`` or a
        *webassets_conf* with a valid ``cachedir``, even if the value points
        to the system's temporary folder.

    :confkey:`default_format` :faint:`[default=None]`
        The default format of files where the :term:`template format` could
        not be determined automatically. This must be the name of another,
        registered format.

    :confkey:`engine.*`
        All keys starting with ``engine.`` will be registered as engines. For
        example, if the key ``engine.php`` is provided, the engine will be
        instantiated via :func:`score.init.init_object` and registered for the
        extension ``php``.
    """
    conf = dict(defaults.items())
    conf.update(confdict)
    if not conf['cachedir'] and webassets_conf and webassets_conf.cachedir:
        conf['cachedir'] = os.path.join(webassets_conf.cachedir, 'tpl')
    if conf['cachedir']:
        init_cache_folder(conf, 'cachedir', autopurge=True)
    if conf['rootdir']:
        assert os.path.isdir(conf['rootdir'])
    renderer = Renderer(conf['rootdir'], conf['cachedir'],
                        conf['default_format'])
    extensions = set()
    for key in extract_conf(conf, 'engine.'):
        extensions.add(key.split('.', 1)[0])
    for ext in extensions:
        engine = init_object(conf, 'engine.' + ext)
        renderer.register_engine(ext, engine)
    return ConfiguredTplModule(renderer, conf['rootdir'],
                               conf['cachedir'], conf['default_format'])


class ConfiguredTplModule(ConfiguredModule):
    """
    This module's :class:`configuration class
    <score.init.ConfiguredModule>`.
    """

    def __init__(self, renderer, rootdir, cachedir, default_format):
        super().__init__(__package__)
        self.renderer = renderer
        self.rootdir = rootdir
        self.cachedir = cachedir
        self.default_format = default_format


class TemplateConverter:
    """
    The default :term:`template converter`, which always returns the
    unmodified input.
    """

    def __init__(self, rootdir, encoding):
        self.rootdir = rootdir
        self.encoding = encoding

    def convert_file(self, path):
        """
        Converts a *path* by searching the appropriate file in the configured
        root folder and returning its contents.
        """
        bincontent = open(os.path.join(self.rootdir, path), 'rb').read()
        if self.encoding == 'binary':
            return bincontent
        return str(bincontent, self.encoding)

    def convert_string(self, string, path=None):
        """
        Returns the input string, optionally converting to binary, if that was
        the configured encoding. The optional parameter *path* will be passed
        if the input *string* was generated by an engine that processed the
        given path. This function ignores this parameter, though.
        """
        if self.encoding == 'binary' and isinstance(string, str):
            string = string.encode('UTF-8')
        return string


class Renderer:
    """
    Central class, which manages template rendering. This class manages two
    distinct template properties: :term:`template engines <template engine>`
    and :term:`template formats <template format>`.

    After registering a file format via :meth:`.register_format`, the renderer
    accepts functions, filters and global variables for that format. It is
    thus possible to expose certain features to specific file formats only.

    Rendering a template is done with :meth:`.Renderer.render_file` or
    :meth:`.Renderer.render_string`. Whereas the former function extracts
    the template format and the engine to use from the file extension, the
    latter needs those two properties explicitly.
    """

    def __init__(self, rootdir, cachedir, default_format):
        self.rootdir = rootdir
        self.cachedir = cachedir
        self.default_format = default_format
        self.engines = {}
        self.functions = {}
        self.filters = {}
        self.globals_ = {}
        self.subrenderers = {}
        self.formats = {}

    def register_engine(self, extension, engine):
        """
        Registers an :term:`engine <template engine>` to use for given file
        *extension*.
        """
        assert extension not in self.engines
        self.engines[extension] = engine

    def register_format(self, name, rootdir=None, cachedir=None,
                        converter=None, encoding='utf-8'):
        """
        Registers a :term:`template format <template format>`. This new format
        can have a specific *rootdir* and *cachedir*. The fallback for either
        value is a sub-folder with the format's *name* within the folder of the
        module configuration.

        An optional :term:`converter <template converter>` can be provided to
        transform the engine output.

        The default converter assumes that all files are encoded as UTF-8.
        This default can be overridden using *encoding*. One special value
        this parameter accepts is ``binary``, which will cause the templates
        to return `binary` objects instead of `str`.
        """
        if not rootdir:
            if not self.rootdir:
                raise ValueError(
                    'Neither generic, nor format-specific `rootdir` found')
            rootdir = os.path.join(self.rootdir, name)
        if not cachedir and self.cachedir:
            cachedir = os.path.join(self.cachedir, name)
        if not converter:
            converter = TemplateConverter(rootdir, encoding)
        self.functions[name] = {}
        self.filters[name] = {}
        self.globals_[name] = {}
        self.formats[name] = (rootdir, cachedir, converter, encoding)

    def format_rootdir(self, format):
        """
        Returns the root folder of given *format*.
        See :meth:`.register_format`.
        """
        return self.formats[format][0]

    def format_cachedir(self, format):
        """
        Returns the cache folder of given *format*.
        See :meth:`.register_format`.
        """
        return self.formats[format][1]

    def format_converter(self, format):
        """
        Returns the :term:`template converter` of given *format*.
        See :meth:`.register_format`.
        """
        return self.formats[format][2]

    def format_encoding(self, format):
        """
        Returns the file encoding of files in specified *format*.
        See :meth:`.register_format`.
        """
        return self.formats[format][3]

    def paths(self, format, virtassets, includehidden=False):
        """
        Provides all available paths for given *format*. Will include all
        :term:`paths <asset path>` of requested :term:`template format`, as
        well as all paths in given :class:`virtassets
        <score.webassets.VirtualAssets>`.

        If the parameter *includehidden* is False, the function will omit all
        paths, where the file name or any of the folder names start with an
        underscore.

        See the :ref:`narrative documentation of the rendering process
        <tpl_rendering>` to learn which files will be returned exactly.
        """
        extensions = ['.%s' % format]
        for ext in self.engines:
            extensions.append('.%s.%s' % (format, ext))
            if format == self.default_format:
                extensions.append('.%s' % ext)
        paths = list(virtassets.paths()) if virtassets else []
        if not includehidden:
            paths = [p for p in paths if p[0] != '_' and '/_' not in p]
        for parent, folders, files in os.walk(self.format_rootdir(format), followlinks=True):
            for folder in folders[:]:
                if folder[0] == '_':
                    folders.remove(folder)
            for file in files:
                if not includehidden and file[0] == '_':
                    continue
                foundext = False
                for ext in extensions:
                    if file.endswith(ext):
                        foundext = True
                        break
                if not foundext:
                    continue
                fullpath = os.path.join(parent, file)
                if not os.path.exists(fullpath):
                    log.warn('Unreadable asset path: ' + fullpath)
                    continue
                relpath = os.path.relpath(fullpath, self.format_rootdir(format))
                paths.append(relpath)
        return paths

    def add_function(self, format, name, callback, *, escape_output=True):
        """
        Registers a *callback* function, that is available with given *name*
        in templates of given *format*. The *format* must have been
        registered via :meth:`.register_format` earlier.

        The keyword-only argument *escape_output* specifies whether the output
        of this function needs to be escaped.
        """
        assert format in self.functions
        assert name not in self.functions[format]
        self.functions[format][name] = (callback, escape_output)
        for key in self.subrenderers:
            self.subrenderers[key].add_function(name, callback, escape_output)

    def add_filter(self, format, name, callback, *, escape_output=True):
        """
        Registers a *callback* function, that is available with given *name*
        in templates of given *format* as a :term:`filter`. The *format*
        must have been registered via :meth:`.register_format` earlier.

        The keyword-only argument *escape_output* specifies whether the output
        of this function needs to be escaped.
        """
        assert format in self.filters
        assert name not in self.filters[format]
        self.filters[format][name] = (callback, escape_output)
        for key in self.subrenderers:
            self.subrenderers[key].add_filter(name, callback, escape_output)

    def add_global(self, format, name, value):
        """
        Registers a variable, that is always available with given *name*
        in templates of given *format*. The *format* must have been
        registered via :meth:`.register_format` earlier.
        """
        assert format in self.globals_
        assert name not in self.globals_[format]
        self.globals_[format][name] = value
        for key in self.subrenderers:
            self.subrenderers[key].add_global(name, value)

    def render_file(self, file, variables={}):
        """
        Renders given template *file* with the provided `dict` of *variables*,
        mapping name to value. This function will determine the
        :term:`template format` and the :term:`template engine` to use using
        the file's extension(s), as explained in the :ref:`narrative
        documentation of the rendering process <tpl_rendering>`.

        If the template format cannot be determined and no ``default_format``
        was configured, a ValueError is raised.
        """
        parts = file.rsplit('.', 2)
        if len(parts) == 2:
            ext = parts[1]
            if ext in self.formats and ext in self.engines:
                raise ValueError("Ambiguous file extension `%s`: it's both a format and an engine." % ext)
            if ext in self.formats:
                return self.format_converter(ext).convert_file(file)
            elif not self.default_format:
                raise ValueError("Could not determine file format of '%s'." % file)
            elif ext not in self.engines:
                return self.format_converter(self.default_format).convert_file(file)
            else:
                format, engine = self.default_format, ext
        elif len(parts) == 3:
            _, format, engine = parts
            if format not in self.formats:
                if not self.default_format:
                    raise ValueError("Could not determine file format of '%s'." % file)
                format = self.default_format
            if engine not in self.engines:
                return self.format_converter(self.default_format).convert_file(file)
        else:
            if not self.default_format:
                raise ValueError("Could not determine file format of '%s'." % file)
            return self.format_converter(self.default_format).convert_file(file)
        result = self.subrenderer(format, engine).render_file(file, variables)
        return self.format_converter(format).convert_string(result, file)

    def render_string(self, string, format, engine, variables={}):
        """
        Renders given template *string* with the provided `dict` of
        *variables*, mapping name to value. Unlike the :meth:`render_file`
        method, this function needs the template *format* and the template
        *engine* explicitly.

        See the :ref:`narrative documentation of the rendering process
        <tpl_rendering>` for details.
        """
        return self.subrenderer(format, engine).render_string(string, variables)

    def subrenderer(self, format, engine):
        """
        Returns an :class:`.EngineRenderer` for given *format* and *engine*.
        """
        key = (format, engine)
        try:
            return self.subrenderers[key]
        except KeyError:
            pass
        args = format, self.format_rootdir(format), self.format_cachedir(format)
        subrenderer = self.engines[engine].create_subrenderer(*args)
        for name in self.functions[format]:
            callback, escape_output = self.functions[format][name]
            subrenderer.add_function(name, callback, escape_output)
        for name in self.filters[format]:
            callback, escape_output = self.filters[format][name]
            subrenderer.add_filter(name, callback, escape_output)
        for name in self.globals_[format]:
            subrenderer.add_global(name, self.globals_[format][name])
        self.subrenderers[key] = subrenderer
        return subrenderer


class Engine(metaclass=ABCMeta):
    """
    Abstract base class for :term:`template engines <template engine>`. The
    sole duty of this class is to create :class:`EngineRenderers
    <.EngineRenderer>` for specific
    :term:`template formats <template format>`.
    """

    @abstractmethod
    def create_subrenderer(format, rootdir, cachedir):
        """
        Creates a new :class:`.EngineRenderer` object for given
        :term:`template format`. The :class:`Renderer <score.tpl.Renderer>`
        will call this only once for each file format.
        """
        return


class EngineRenderer(metaclass=ABCMeta):
    """
    Abstract base class for sub-renderers created by
    :meth:`Engine.create_subrenderer`. This class is only relevant when
    implementing a new :term:`template engine`.

    Instances of this class can make these assumptions:

    - All registered entities (i.e. functions, filters and globals) will only
      be registered once.
    - The :class:`Renderer <score.tpl.Renderer>` will further ensure there are
      no name collisions.
    - There will be only one instance per engine/format combination.
    """

    @abstractmethod
    def add_function(self, name, callback, escape_output=True):
        """
        Adds a function that shall be available globally.
        """
        return

    @abstractmethod
    def add_filter(self, name, callback, escape_output=True):
        """
        Adds a :term:`filter` that shall be available globally.
        """
        return

    @abstractmethod
    def add_global(self, name, value):
        """
        Adds a variable that shall be available globally.
        """
        return

    @abstractmethod
    def render_file(self, file, variables):
        """
        Renders given template *file* with the given *variables* dict.
        """
        return

    @abstractmethod
    def render_string(self, string, variables):
        """
        Renders given template *string* with the given *variables* dict.
        """
        return
