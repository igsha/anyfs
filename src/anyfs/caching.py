from pathlib import Path
import shutil
from urllib.request import Request, urlopen


class FileCache:
    def __init__(self, url, tempdir):
        self.url = url
        self.tempfile = Path(tempdir).joinpath(url.replace("/", "-").replace(":", "-"))
        self._size = None
        self.iscached = False
        self.fp = None

    def open(self):
        if not self.iscached:
            with urlopen(self.url) as resp, open(self.tempfile, "wb") as f:
                shutil.copyfileobj(resp, f)

            self.iscached = True

            if self._size is None:
                self._size = self.tempfile.stat().st_size
            else:
                assert(self._size == self.tempfile.stat().st_size)

        self.fp = open(self.tempfile, "rb")

    def close(self):
        self.fp.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            assert(idx.step is None or idx.step == 1)
            pos = idx.start if idx.start is not None else 0
            size = idx.stop - idx.start if idx.stop is not None else -1
        else:
            pos = idx
            size = -1

        self.fp.seek(pos)
        return self.fp.read(size)

    def __len__(self):
        if self._size is None:
            r = Request(self.url, method="HEAD")
            with urlopen(r) as f:
                self._size = int(f.getheader("Content-Length"))

        return self._size


if __name__ == "__main__":
    import tempfile

    testurl = "https://pic.rutubelist.ru/video/3a/c2/3ac2fd23314dfb81ed877e6c75584ffc.jpg"
    with tempfile.TemporaryDirectory() as tempdir:
        fc = FileCache(testurl, tempdir)
        print("Tempfile", fc.tempfile)
        print("Size:", len(fc))
        fc.open()
        print("4 bytes starting from 6:", fc[6:10])
        fc.close()

    with tempfile.TemporaryDirectory() as tempdir, FileCache(testurl, tempdir) as fc:
        print("Tempfile", fc.tempfile)
        print("Size:", len(fc))
        print("4 bytes starting from 6:", fc[6:10])
