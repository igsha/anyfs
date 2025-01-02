import argparse
import fuse
import os

from .mystat import MyStat
from .protocol import Protocol
from .caching import FileCache


fuse.fuse_python_api = (0, 2)


class AnyFS(fuse.Fuse):
    # ostream should be opened the first
    def __init__(self, istream, ostream, tmpdir, *args, **kwargs):
        super(AnyFS, self).__init__(*args, **kwargs)
        self.protocol = Protocol(istream, ostream, tmpdir)
        self.openedfd = {}

    def getattr(self, path):
        t = self.protocol.take(path)
        if isinstance(t, list):
            return MyStat.dir()
        elif isinstance(t, bytes) or isinstance(t, FileCache):
            return MyStat.file(len(t))
        else:
            return -fuse.ENOENT

    def readdir(self, path, offset):
        t = self.protocol.take(path)
        if isinstance(t, list):
            for r in  ['.', '..', *t]:
                yield fuse.Direntry(r)
        else:
            return -fuse.ENOENT

    def open(self, path, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & os.O_RDONLY) != os.O_RDONLY:
            return -fuse.EACCES

        obj = self.protocol.take(path)
        if isinstance(obj, FileCache):
            obj.open()
            self.openedfd[path] = obj

        return 0

    def release(self, path, flags):
        if path in self.openedfd:
            self.openedfd[path].close()
            del self.openedfd[path]

        return 0

    def read(self, path, size, offset):
        if path in self.openedfd:
            t = self.openedfd[path]
        else:
            t = self.protocol.take(path)
            if not isinstance(t, bytes):
                return -fuse.EISDIR

        return t[min(offset, len(t)):min(offset + size, len(t))]
