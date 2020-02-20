# Copyright © 2015-2018 STRG.AT GmbH, Vienna, Austria
# Copyright © 2020 Necdet Can Ateşman, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in
# the file named COPYING.LESSER.txt.
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
# the discretion of STRG.AT GmbH also the competent court, in whose district
# the Licensee has his registered seat, an establishment or assets.

from ._exc import TemplateNotFound
import abc
import os
import xxhash


class Loader:
    """
    Object capable of loading template content.
    """

    @property
    def paths(self):
        return list(self.iter_paths())

    @abc.abstractmethod
    def iter_paths(self):
        """
        Provide a generator iterating all valid paths of this loader.
        """
        pass

    @abc.abstractmethod
    def load(self, path):
        """
        Load given *path*. Returns a 2-tuple, where the first value is a `bool`
        indicating whether the other value is a file path (`True`) or the
        contents of the template (`False`). Illustration of the return values:

        .. code-block:: python

            (True, '/path/to/the/template.html')
            (False, '<html>The contents of the template</html>')

        Raises :class:`TemplateNotFound` if this loader cannot load the given
        path.
        """
        pass

    def is_valid(self, path):
        """
        Whether given *path* is valid for this loader, i.e. whether a call to
        :meth:`load` would return successfully.
        """
        return path in self.iter_paths()

    def hash(self, path):
        """
        Provides a random `str`, that will always change whenever the file
        content changes. The default implementation uses the content's xxHash_.

        .. _xxHash: http://cyan4973.github.io/xxHash/
        """
        is_file, result = self.load(path)
        if is_file:
            try:
                hash = xxhash.xxh64()
                with open(result, 'rb') as file:
                    for chunk in iter(lambda: file.read(4096), b""):
                        hash.update(chunk)
                return hash.hexdigest()
            except FileNotFoundError:
                raise TemplateNotFound(path)
        else:
            if isinstance(result, str):
                result = result.encode('ASCII')
            return xxhash.xxh64(result).hexdigest()


class FileSystemLoader(Loader):
    """
    :class:`Loader` searching for files with a given *extension* inside given
    folders.
    """

    def __init__(self, rootdirs, extension):
        if isinstance(rootdirs, str):
            rootdirs = [rootdirs]
        self.rootdirs = rootdirs
        self.extension = extension

    def is_valid(self, path):
        return bool(self._find_file(path))

    def iter_paths(self):
        if not self.rootdirs:
            return
        found = []
        ext = '.%s' % (self.extension,)
        extlen = len(ext)
        for rootdir in self.rootdirs:
            for base, dirs, files in os.walk(rootdir, followlinks=True):
                base = os.path.relpath(base, rootdir)
                if base == '.':
                    base = ''
                else:
                    base = base + '/'
                for filename in files:
                    if filename[-extlen:] != ext:
                        continue
                    path = base + filename
                    if path in found:
                        continue
                    found.append(path)
                    yield path

    def load(self, path):
        file = self._find_file(path)
        if file:
            return True, file
        raise TemplateNotFound(path)

    def _find_file(self, path):
        for rootdir in self.rootdirs:
            fullpath = os.path.join(rootdir, path.lstrip('/'))
            relpath = os.path.relpath(fullpath, rootdir)
            if relpath.startswith(os.pardir + os.sep):
                # outside of rootdir
                continue
            if os.path.exists(fullpath):
                return fullpath
        return None


class ChainLoader(Loader):
    """
    A :class:`Loader` that will wrap the other given *loaders* and simulate a
    loader, that combines the features of all of them. If this receives a
    Loader capable of loading 'a.tpl' and another Loader that can load 'b.tpl',
    this ChainLoader instance will be able to load 'a.tpl' *and* 'b.tpl'.
    """

    def __init__(self, loaders):
        self.loaders = loaders

    def is_valid(self, path):
        return any(loader.is_valid(path) for loader in self.loaders)

    def iter_paths(self):
        for loader in self.loaders:
            yield from loader.iter_paths()

    def load(self, path):
        for loader in self.loaders:
            try:
                return loader.load(path)
            except TemplateNotFound:
                pass
        raise TemplateNotFound(path)

    def hash(self, path):
        for loader in self.loaders:
            try:
                return loader.hash(path)
            except TemplateNotFound:
                pass


class PrefixedLoader(Loader):
    """
    A :class:`Loader` wrapper, that prefixes a pre-given path to all templates.
    If this is configured with the prefix 'foo/' and given a loader capable of
    loading 'a.tpl', the resulting instance will only be able to load
    'foo/a.tpl' (but not 'a.tpl').

    Note that this loader does not modify the given prefix. It is important to
    add a slash to the prefix, if you want it to behave like a folder, for
    example.
    """

    def __init__(self, prefix, wrapped):
        self.prefix = prefix
        self.wrapped = wrapped

    def iter_paths(self):
        yield from (self.prefix + path for path in self.wrapped.iter_paths())

    def load(self, path):
        if not path.startswith(self.prefix):
            raise TemplateNotFound(path)
        return self.wrapped.load(path[len(self.prefix):])

    def is_valid(self, path):
        if not path.startswith(self.prefix):
            return False
        return self.wrapped.is_valid(path[len(self.prefix):])

    def hash(self, path):
        if not path.startswith(self.prefix):
            raise TemplateNotFound(path)
        return self.wrapped.hash(path[len(self.prefix):])
