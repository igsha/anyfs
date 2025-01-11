from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError


class ContentCache:
    def __init__(self, url, tempdir):
        self.url = url
        self.tempdir = tempdir
        self.tempfile = None
        self._size = None
        self.iscached = False

        domain = urlparse(url)._replace(path="", params="", query="", fragment="")
        self.headers = dict(referer=domain.geturl())

    def open(self):
        if self.tempfile is None:
            r = Request(self.url, headers=self.headers)
            try:
                with urlopen(r) as resp, NamedTemporaryFile(mode="wb", dir=self.tempdir, delete=False) as f:
                    shutil.copyfileobj(resp, f)
                    self.tempfile = Path(f.name)
            except HTTPError as ex:
                if ex.code == 404:
                    print("Not found resource", self.url)

                raise

            if self._size is None:
                self._size = self.tempfile.stat().st_size
            else:
                assert(self._size == self.tempfile.stat().st_size)

        return open(self.tempfile, "rb")

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            assert(idx.step is None or idx.step == 1)
            pos = idx.start if idx.start is not None else 0
            size = idx.stop - idx.start if idx.stop is not None else -1
        else:
            pos = idx
            size = -1

        with self.open() as fp:
            fp.seek(pos)
            return fp.read(size)

    def __len__(self):
        if self._size is None:
            r = Request(self.url, method="HEAD", headers=self.headers)
            try:
                with urlopen(r) as f:
                    self._size = int(f.getheader("Content-Length"))
            except Exception as ex:
                return 0

        return self._size


if __name__ == "__main__":
    import tempfile

    testurl = "https://pic.rutubelist.ru/video/3a/c2/3ac2fd23314dfb81ed877e6c75584ffc.jpg"
    with tempfile.TemporaryDirectory() as tempdir:
        fc = ContentCache(testurl, tempdir)
        print("Tempfile", fc.tempfile)
        print("Size:", len(fc))
        print("4 bytes starting from 6:", fc[6:10])
