import requests
from sortedcontainers import SortedDict
from tempfile import NamedTemporaryFile

from .cachedfile import CachedFile


class ContentCache:
    def __init__(self, session, url, tempdir, headers={}):
        self.session = session
        self.url = url
        self.headers = headers
        self.size = None

        ext = url.rfind(".")
        ext = url[ext:] if ext != -1 else ".bin"
        self.tempfile = NamedTemporaryFile(mode="w+b", suffix=ext, dir=tempdir, delete=False)
        self.chunks = SortedDict()

    @staticmethod
    def newSession():
        return requests.Session()

    def open(self):
        return CachedFile(self.session, self.url, self.headers, self.tempfile.name, self.chunks)

    def __len__(self):
        if self.size is not None:
            return self.size

        for method in ["HEAD", "GET"]:
            req = requests.Request(method, self.url, self.headers)
            with self.session.send(req.prepare(), stream=True) as r:
                if not r.ok:
                    continue

                try:
                    self.size = int(r.headers["content-length"])
                    return self.size
                except KeyError:
                    print("KEYERROR:", r.headers)

        return None
