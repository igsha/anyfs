import atexit
import tempfile

from .caching import ContentCache


class Communicator:
    def __init__(self, istream, ostream):
        self.istream = istream
        self.ostream = ostream
        self.tmpdir = tempfile.TemporaryDirectory(prefix="anyfs-")
        atexit.register(self.cleanup)

    def cleanup(self):
        self.tmpdir.cleanup()

    def fetch(self, path):
        self.ostream.write(f"{path}\n".encode())
        self.ostream.flush()

        while t := self.istream.readline().strip().decode():
            tpl = t.split(" ", 1)
            cmd = tpl[0]
            if cmd == "bytes":
                count, filepath = tpl[1].split(" ", 1)
                yield filepath, self.istream.read(int(count))
            elif cmd == "entity":
                yield tpl[1], []
            elif cmd == "url":
                count, filepath = tpl[1].split(" ", 1)
                url = self.istream.readline().strip().decode()
                headers = {}
                for _ in range(int(count)):
                    key, value = self.istream.readline().strip().decode().split(":", 1)
                    headers[key] = value

                yield filepath, ContentCache(url, self.tmpdir.name, headers)
            elif cmd == "link":
                yield tpl[1], self.istream.readline().strip().decode()
            elif cmd == "eom":
                break
            elif cmd == "notfound":
                yield tpl[1], None
            elif cmd == "ioerror":
                yield tpl[1], IOError("network failure")
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
        return self.map.get(path, None)
