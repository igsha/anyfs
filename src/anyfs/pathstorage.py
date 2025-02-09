import os


class PathStorage:
    def __init__(self, communicator):
        self.communicator = communicator
        self.map = {}
        self.tsmap = {}

    def _appendToParent(self, path):
        if path == "/":
            return

        parent, child = os.path.split(path)
        if parent not in self.map:
            self._appendToParent(parent)
            self.map[parent] = []
        elif child in self.map[parent]:
            return

        self.map[parent].append(child)

    def _updateTimestamp(self, path, timestamp):
        if path in self.tsmap:
            timestamp = min(self.tsmap[path], timestamp)

        self.tsmap[path] = timestamp
        if path != "/":
            parent, _ = os.path.split(path)
            self._updateTimestamp(parent, timestamp)

    def _fetch(self, path):
        for p, ts, val in self.communicator.fetch(path):
            if val is None or isinstance(val, IOError):
                return

            if not isinstance(val, self.communicator.Incomplete):
                self.map[p] = val

            self._updateTimestamp(p, ts)
            self._appendToParent(p)
            if isinstance(val, str):
                self._appendToParent(val)

    def get(self, path):
        path = path.strip()
        if len(path) > 2:
            path = path.rstrip("/")

        if path in self.map:
            return self.map[path]

        cur = "/"
        prev = [""]
        for p in path.split("/"):
            cur = os.path.join(cur, p)
            if cur in self.map:
                pass
            elif p in prev:
                self._fetch(cur)
            else:
                return None

            prev = self.map[cur]

        return self.map.get(path, None)

    def gettimestamp(self, path):
        return self.tsmap.get(path, None)

    def __item__(self, path):
        return self.get(path)
