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
    def _extract(ts, cmd, argstr, n):
        if cmd[0] == "t":
            tpl = argstr.split(" ", n)
            tpl[0] = int(tpl[0]) # timestamp is int
            return tpl
        else:
            return ts, *argstr.split(" ", n - 1)

    def _fetchurl(self, cmd, rest, timestamp):
        counturls = 1
        if cmd[-1] == "s":
            timestamp, counturls, counthdrs, filepath = self._extract(timestamp, cmd, rest, 3)
        else:
            timestamp, counthdrs, filepath = self._extract(timestamp, cmd, rest, 2)

        urls = [self.istream.readline().strip().decode() for _ in range(int(counturls))]
        headers = {}
        for _ in range(int(counthdrs)):
            key, value = self.istream.readline().strip().decode().split(":", 1)
            headers[key] = value

        return filepath, timestamp, ContentCache(urls, self.tmpdir.name, headers)

    def fetch(self, path):
        self.ostream.write(f"{path}\n".encode())
        self.ostream.flush()

        while t := self.istream.readline().strip().decode():
            tpl = t.split(" ", 1)
            cmd = tpl[0]
            timestamp = self.curtime
            if cmd == "bytes" or cmd == "tbytes":
                timestamp, count, filepath = self._extract(timestamp, cmd, tpl[1], 2)
                yield filepath, timestamp, self.istream.read(int(count))
            elif cmd == "entity" or cmd == "tentity":
                timestamp, filepath = self._extract(timestamp, cmd, tpl[1], 1)
                yield filepath, timestamp, self.Incomplete()
            elif cmd == "url" or cmd == "turl" or cmd == "urls" or cmd == "turls":
                yield self._fetchurl(cmd, tpl[1], timestamp)
            elif cmd == "link" or cmd == "tlink":
                timestamp, filepath = self._extract(timestamp, cmd, tpl[1], 1)
                yield filepath, timestamp, self.istream.readline().strip().decode()
            elif cmd == "eom":
                break
            elif cmd == "notfound":
                yield tpl[1], timestamp, None
            elif cmd == "ioerror":
                yield tpl[1], timestamp, IOError("network failure")
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
