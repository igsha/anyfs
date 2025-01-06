import argparse
import fuse
import os

from .caching import FileCache
from .mystat import MyStat
from .pathmap import PathMap
from .protocol import Protocol


fuse.fuse_python_api = (0, 2)


class AnyFS(fuse.Fuse):
    # ostream should be opened the first
    def __init__(self, istream, ostream, tmpdir, *args, **kwargs):
        super(AnyFS, self).__init__(*args, **kwargs)
        protocol = Protocol(istream, ostream, tmpdir)
        self.map = PathMap(protocol)

    def getattr(self, path):
        t = self.map.get(path)
        if isinstance(t, list):
            return MyStat.dir()
        elif isinstance(t, bytes) or isinstance(t, FileCache):
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
        if isinstance(obj, FileCache):
            obj.open()

        return 0

    def release(self, path, flags):
        obj = self.map.get(path)
        if isinstance(obj, FileCache):
            obj.close()

        return 0

    def read(self, path, size, offset):
        t = self.map.get(path)
        if isinstance(t, list):
            return -fuse.EISDIR

        return t[min(offset, len(t)):min(offset + size, len(t))]
