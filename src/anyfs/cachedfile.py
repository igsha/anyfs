from bisect import bisect
from sortedcontainers import SortedDict


class CachedFile:
    def __init__(self, session, url, headers, filename, chunks: SortedDict):
        self.session = session
        self.url = url
        self.headers = headers
        self.chunks = chunks

        self.connection = None
        self.strpos = 0
        self.position = 0
        self.fp = open(filename, "r+b")

    def _reconnect(self, chunk):
        if self.connection is not None:
            self.connection.close()

        headers = self.headers.copy()
        headers["range"] = f"bytes={chunk[0]}-"
        self.connection = self.session.get(self.url, headers=headers, stream=True)
        if self.connection.status_code not in [206, 200]:
            raise RuntimeError(f"NetworkFile: Error={self.connection.status_code}, Reason={self.connection.reason}", chunk)

        # partial content is not supported => cache all content
        if self.connection.status_code != 206:
            chunk = (0, int(self.connection.headers['content-length']))
            self.chunks.clear()
            self.chunks[chunk[0]] = chunk[1]

        return chunk

    def _getchunk(self, first, last):
        idx = bisect(self.chunks.keys(), first)
        if idx > 0:
            pfirst, plast = self.chunks.peekitem(idx-1)
            if first < plast:
                first = plast

        idx = bisect(self.chunks.keys(), last)
        if idx > 0:
            pfirst, plast = self.chunks.peekitem(idx-1)
            if last <= plast:
                last = pfirst

        return (first, last) if first < last else None

    def _insertchunk(self, first, last):
        inserted = False
        for k, v in self.chunks.items():
            if v == first:
                self.chunks[k] = last
                inserted = True
            elif k >= first and v <= last:
                del self.chunks[k]

        if not inserted:
            self.chunks[first] = last

    def seek(self, position):
        self.position = position

    def read(self, size):
        # should be protected by mutex?
        chunk = self._getchunk(self.position, self.position + size)
        if chunk is not None:
            if self.strpos != chunk[0] or self.connection is None:
                chunk = self._reconnect(chunk)

            # suppose that the chunk size is not big enough to exhaust all memory
            buf = self.connection.raw.read(chunk[1] - chunk[0])
            self.fp.seek(chunk[0])
            self.fp.write(buf)
            self.fp.flush()
            self.strpos = chunk[1]
            self._insertchunk(*chunk)
            # chunk not always == (first, last) => reread from cache

        self.fp.seek(self.position)
        buf = self.fp.read(size)
        return buf

    def close(self):
        if self.connection is not None:
            self.connection.close()

        self.fp.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()


if __name__ == "__main__":
    import requests
    from tempfile import NamedTemporaryFile

    wikiurl = "https://upload.wikimedia.org/wikipedia/commons/8/8c/Cow_%28Fleckvieh_breed%29_Oeschinensee_Slaunger_2009-07-07.jpg"
    wikiheaders = {"user-agent": "Curl/1.0"}
    testchunks = [(6, 10), (50, 50+45), (150, 150+10), (160, 160+10), (0, 100)]

    with requests.get(wikiurl, stream=True, headers=wikiheaders) as f:
        truedata = f.raw.read(200)

    with NamedTemporaryFile() as temp, requests.Session() as sess:
        chunks = SortedDict()
        with CachedFile(sess, wikiurl, wikiheaders, temp.name, chunks) as f:
            for (first, last) in testchunks:
                f.seek(first)
                print("fetch", first, last)
                buf = f.read(last - first)
                assert truedata[first:last] == buf, f"chunk {first}:{last}"

        print("Result chunks:", chunks)
