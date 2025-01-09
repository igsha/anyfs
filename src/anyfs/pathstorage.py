import os


class PathStorage:
    def __init__(self, communicator):
        self.communicator = communicator
        self.map = {}

    def _appendToParent(self, path):
        parent, child = os.path.split(path)
        if parent not in self.map:
            if parent != "/":
                self._appendToParent(parent)

            self.map[parent] = []

        self.map[parent].append(child)

    def _fetch(self, path):
        for p, val in self.communicator.fetch(path):
            self.map[p] = val
            self._appendToParent(p)

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

    def __item__(self, path):
        return self.get(path)
