import fuse
import io
import os
from threading import Lock

from .communicator import Communicator, ContentCache
from .mystat import MyStat
from .pathstorage import PathStorage


fuse.fuse_python_api = (0, 2)


class AnyFS(fuse.Fuse):
    # ostream should be opened the first
    def __init__(self, istream, ostream, *args, **kwargs):
        super().__init__(*args, **kwargs)
        communicator = Communicator(istream, ostream)
        self.storage = PathStorage(communicator)
        self.file_class = self._fileClass()

    def _fileClass(parent):
        class FileHandler(object):
            def __init__(self, path, flags, *mode):
                obj = parent.storage.get(path)
                if isinstance(obj, ContentCache):
                    self.fp = obj.open()
                elif isinstance(obj, bytes):
                    self.fp = io.BytesIO(obj)
                else:
                    raise RuntimeError("Not a file-like object")

                self.mutex = Lock()

            def release(self, flags):
                self.fp.close()

            def read(self, size, offset):
                with self.mutex:
                    self.fp.seek(offset)
                    return self.fp.read(size)

        return FileHandler

    def getattr(self, path):
        t = self.storage.get(path)
        if isinstance(t, list):
            return MyStat.dir()
        elif isinstance(t, bytes) or isinstance(t, ContentCache):
            return MyStat.file(len(t))
        elif isinstance(t, str):
            return MyStat.link()
        else:
            return -fuse.ENOENT

    def readdir(self, path, offset):
        t = self.storage.get(path)
        if isinstance(t, list):
            for r in  ['.', '..', *t]:
                yield fuse.Direntry(r)
        else:
            return -fuse.ENOENT

    def readlink(self, path):
        t = self.storage.get(path)
        if isinstance(t, str):
            return os.path.join(self.fuse_args.mountpoint, t[1:])
        else:
            return -fuse.ENODEV
