import fuse
import io
import os

from .communicator import Communicator, ContentCache
from .mystat import MyStat
from .pathstorage import PathStorage


fuse.fuse_python_api = (0, 2)


class AnyFS(fuse.Fuse):
    # ostream should be opened the first
    def __init__(self, istream, ostream, *args, **kwargs):
        super(AnyFS, self).__init__(*args, **kwargs)
        communicator = Communicator(istream, ostream)
        self.map = PathStorage(communicator)
        self.file_class = self._fileClass()

    def _fileClass(parent):
        class FileHandler(object):
            def __init__(self, path, flags, *mode):
                obj = parent.map.get(path)
                if isinstance(obj, ContentCache):
                    self.fp = obj.open()
                elif isinstance(obj, bytes):
                    self.fp = io.BytesIO(obj)
                else:
                    raise RuntimeError("Not a bytes-like object")

            def release(self, flags):
                self.fp.close()

            def read(self, size, offset):
                self.fp.seek(offset)
                return self.fp.read(size)

        return FileHandler

    def getattr(self, path):
        t = self.map.get(path)
        if isinstance(t, list):
            return MyStat.dir()
        elif isinstance(t, bytes) or isinstance(t, ContentCache):
            return MyStat.file(len(t))
        else:
            return -fuse.ENOENT

    def readdir(self, path, offset):
        t = self.map.get(path)
        if isinstance(t, list):
            for r in  ['.', '..', *t]:
                yield fuse.Direntry(r)
        else:
            return -fuse.ENOENT
