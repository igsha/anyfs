import fuse
import os

from .caching import ContentCache
from .communicator import Communicator
from .mystat import MyStat
from .pathstorage import PathStorage


fuse.fuse_python_api = (0, 2)


class AnyFS(fuse.Fuse):
    # ostream should be opened the first
    def __init__(self, istream, ostream, *args, **kwargs):
        super(AnyFS, self).__init__(*args, **kwargs)
        communicator = Communicator(istream, ostream)
        self.map = PathStorage(communicator)

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

    def open(self, path, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & os.O_RDONLY) != os.O_RDONLY:
            return -fuse.EACCES

        obj = self.map.get(path)
        if isinstance(obj, ContentCache):
            obj.open()

        return 0

    def release(self, path, flags):
        obj = self.map.get(path)
        if isinstance(obj, ContentCache):
            obj.close()

        return 0

    def read(self, path, size, offset):
        t = self.map.get(path)
        if isinstance(t, list):
            return -fuse.EISDIR
        elif isinstance(t, IOError):
            return -fuse.EIO

        return t[min(offset, len(t)):min(offset + size, len(t))]
