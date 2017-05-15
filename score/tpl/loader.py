from ._exc import TemplateNotFound
import abc
import os
import hashlib
import fnmatch


class Loader:

    @property
    def paths(self):
        return list(self.iter_paths())

    @abc.abstractmethod
    def iter_paths(self):
        pass

    @abc.abstractmethod
    def load(self, path):
        pass

    def is_valid(self, path):
        return path in self.iter_paths()

    def hash(self, path):
        is_file, result = self.load(path)
        if is_file:
            try:
                return str(os.path.getmtime(result))
            except FileNotFoundError:
                raise TemplateNotFound(path)
        else:
            if isinstance(result, str):
                result = result.encode('ASCII')
            return hashlib.sha256(result).hexdigest()


class FileSystemLoader(Loader):

    def __init__(self, rootdirs, extension):
        self.rootdirs = rootdirs
        self.extension = extension

    def iter_paths(self):
        if not self.rootdirs:
            return
        found = []
        filter = '*.%s' % (self.extension,)
        for rootdir in self.rootdirs:
            for base, dirs, files in os.walk(rootdir):
                for filename in fnmatch.filter(files, filter):
                    path = os.path.join(base, filename)
                    path = os.path.relpath(path, rootdir)
                    if path in found:
                        continue
                    found.append(path)
                    yield path

    def load(self, path):
        for rootdir in self.rootdirs:
            fullpath = os.path.join(rootdir, path.lstrip('/'))
            relpath = os.path.relpath(fullpath, rootdir)
            if relpath.startswith(os.pardir + os.sep):
                # outside of rootdir
                continue
            if os.path.exists(fullpath):
                return True, fullpath
        raise TemplateNotFound(path)


class ChainLoader(Loader):

    def __init__(self, loaders):
        self.loaders = loaders

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
