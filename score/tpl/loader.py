from ._exc import TemplateNotFound
import abc
import glob
import os
import hashlib


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

    def hash(self, path):
        is_file, result = self.load(path)
        if is_file:
            try:
                return os.path.mtime(result)
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
        for rootdir in self.rootdirs:
            pattern = '%s/**/*.%s' % (glob.escape(rootdir), self.extension)
            for path in glob.glob(pattern, recursive=True):
                path = os.path.relpath(path, rootdir)
                if path in found:
                    continue
                filename = os.path.basename(path)
                if '.' in filename[:-(len(self.extension) + 1)]:
                    # this is not the complete file extension, i.e.
                    # self.extension is 'foo' and filename is 'myfile.bar.foo'
                    continue
                found.append(path)
                yield path

    def load(self, path):
        for rootdir in self.rootdirs:
            fullpath = os.path.join(rootdir, path)
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
