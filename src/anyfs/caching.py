from pathlib import Path
import requests
import shutil
import sys
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError


class NetworkFile:
    def __init__(self, session, req):
        self.session = session
        self.req = req
        self.position = 0

    def seek(self, position):
        self.position = position

    def read(self, size):
        req = self.req.copy()
        req.headers["Range"] = f"bytes={self.position}-{self.position + size - 1}"
        with self.session.send(req) as resp:
            if resp.status_code != 206:
                print(f"NetworkFile: warning, the return code {resp.status_code} != 206", file=sys.stderr)
                result = resp.content[self.position:min(self.position + size, len(resp.content))]
            else:
                result = resp.content

        self.position += len(result)
        return result

    def close(self):
        pass


class ContentCache:
    def __init__(self, session, url, tempdir, headers={}):
        self.session = session
        self.req = requests.Request(method="GET", url=url, headers=headers).prepare()
        self.tempdir = tempdir
        self.tempfile = None
        self.size = None
        self.acceptRanges = False

    @staticmethod
    def newSession():
        return requests.Session()

    def open(self):
        if self.acceptRanges:
            return NetworkFile(self.session, self.req)

        if self.tempfile is None:
            with self.session.send(self.req, stream=True) as r:
                if r.headers.get("accept-ranges", "none") != "none":
                    self.acceptRanges = True
                    return NetworkFile(self.session, self.req)

                ext = self.req.url.split(".")[-1]
                with NamedTemporaryFile(mode="wb", suffix="." + ext, dir=self.tempdir, delete=False) as f:
                    shutil.copyfileobj(r.raw, f)
                    self.tempfile = Path(f.name)

            if self.size is None:
                self.size = self.tempfile.stat().st_size
            else:
                assert(self.size == self.tempfile.stat().st_size)

        return open(self.tempfile, "rb")

    def __len__(self):
        if self.size is not None:
            return self.size

        for method in ["HEAD", "GET"]:
            req = self.req.copy()
            req.prepare_method(method)
            with self.session.send(req) as r:
                if not r.ok:
                    continue

                self.size = int(r.headers["content-length"])
                self.acceptRanges = r.headers.get("accept-ranges", "none") != "none"
                return self.size

        return None


if __name__ == "__main__":
    import tempfile

    testurl = "https://pic.rutubelist.ru/video/3a/c2/3ac2fd23314dfb81ed877e6c75584ffc.jpg"
    with tempfile.TemporaryDirectory() as tempdir, ContentCache.newSession() as sess:
        fc = ContentCache(sess, testurl, tempdir)
        print("Size:", len(fc))
        with fc.open()  as f:
            print("Tempfile", fc.tempfile)
            f.seek(6)
            print("4 bytes starting from 6:", f.read(4))
