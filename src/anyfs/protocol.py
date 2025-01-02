from .caching import FileCache


class Protocol:
    def __init__(self, istream, ostream, tmpdir):
        self.istream = istream
        self.ostream = ostream
        self.tmpdir = tmpdir

    def take(self, path):
        self.ostream.write(f"{path}\n".encode())
        self.ostream.flush()

        t = self.istream.readline().strip().decode()
        (cmd, count) = t.split(" ")
        count = int(count)
        if cmd == "bytes":
            return self.istream.read(count)
        elif cmd == "local":
            filename = self.istream.readline().strip().decode()
            return open(filename, "rb").read()
        elif cmd == "entities":
            return [self.istream.readline().strip().decode() for _ in range(count)]
        elif cmd == "url":
            return FileCache(self.istream.readline().strip().decode(), self.tmpdir)
        elif cmd == "notfound":
            return None
        else:
            raise RuntimeError(f"Unknown command {cmd}")


class FakeProtocol:
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

    def take(self, path):
        return self.map.get(path, None)
