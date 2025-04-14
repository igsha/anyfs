import atexit
from datetime import datetime
import tempfile

from .contentcache import ContentCache


class Communicator:
    class Incomplete:
        pass

    def __init__(self, istream, ostream):
        self.istream = istream
        self.ostream = ostream
        self.tmpdir = tempfile.TemporaryDirectory(prefix="anyfs-")
        self.curtime = int(datetime.now().timestamp())
        atexit.register(self.cleanup)

    def cleanup(self):
        self.tmpdir.cleanup()

    @staticmethod
    def _extract(argstr):
        arg, *rest = argstr.split(" ", 1)
        ret = {}
        while True:
            name, val = arg.split("=", 1)
            ret[name] = val
            if len(rest) == 0:
                break

            if rest[0].startswith("path"):
                arg, rest = rest[0], []
            else:
                arg, *rest = rest[0].split(" ", 1)

        return ret

    def _parsestdargs(self, args):
        timestamp = int(args.get("time", self.curtime))
        filepath = args["path"]
        ishidden = args.get("hide", "false").lower() in ["true", "1", "yes", "on"]
        return filepath, timestamp, ishidden

    def _fetchurl(self, argstr):
        d = self._extract(argstr)
        dflt = self._parsestdargs(d)
        counturls = int(d.get("count", 1))
        counthdrs = int(d.get("headers", 0))

        urls = [self.istream.readline().strip().decode() for _ in range(counturls)]
        headers = {}
        for _ in range(counthdrs):
            key, value = self.istream.readline().strip().decode().split(":", 1)
            headers[key] = value

        return *dflt, ContentCache(urls, self.tmpdir.name, headers)

    # filepath, timestamp, ishidden, Class
    def fetch(self, path):
        self.ostream.write(f"{path}\n".encode())
        self.ostream.flush()

        while t := self.istream.readline().strip().decode():
            cmd, *rest = t.split(" ", 1)
            if cmd == "bytes":
                d = self._extract(rest[0])
                ret = self._parsestdargs(d)
                count = int(d["size"])
                yield *ret, self.istream.read(count)
            elif cmd == "entity":
                ret = self._parsestdargs(self._extract(rest[0]))
                yield *ret, self.Incomplete()
            elif cmd == "url":
                yield self._fetchurl(rest[0])
            elif cmd == "link":
                ret = self._parsestdargs(self._extract(rest[0]))
                yield *ret, self.istream.readline().strip().decode()
            elif cmd == "notfound":
                ret = self._parsestdargs(self._extract(rest[0]))
                yield *ret, None
            elif cmd == "ioerror":
                ret = self._parsestdargs(self._extract(rest[0]))
                yield *ret, IOError("network failure")
            elif cmd == "eom":
                break
            else:
                raise RuntimeError(f"Unknown command {cmd}")


class FakeCommunicator:
    def __init__(self, *args, **kwargs):
        self.map = {
                "/": ["d0", "d1", "f0"],
                "/f0": "1234567890",
                "/d0": ["d2", "f1", "f2"],
                "/d1": [],
                "/d0/f1": "123",
                "/d0/f2": "",
                "/d0/d2": [],
        }

    def fetch(self, path):
        yield self.map.get(path, None)
