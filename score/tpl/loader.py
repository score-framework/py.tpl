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
            return os.path.mtime(result)
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
            pattern = '%s/**/*%s' % (glob.escape(rootdir), self.extension)
            for path in glob.glob(pattern, recursive=True):
                path = os.path.relpath(rootdir, path)
                if path in found:
                    continue
                found.append(path)
                yield path

    def load(self, path):
        for rootdir in self.rootdirs:
            fullpath = os.path.join(rootdir, path)
            relpath = os.path.relpath(rootdir, fullpath)
            if relpath.startswith(os.pardir + os.sep):
                # outside of rootdir
                continue
            if os.path.exists(fullpath):
                return True, fullpath
        raise TemplateNotFound(path)
