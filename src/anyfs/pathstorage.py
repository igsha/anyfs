from dataclasses import dataclass
import os

from .communicator import Incomplete


@dataclass
class PathObject:
    obj: 'typing.Any'
    ishidden: bool
    timestamp: int


class PathStorage:
    def __init__(self, communicator):
        self.communicator = communicator
        self.map = {}

    def _appendToParent(self, path, ishidden, timestamp):
        if path == "/":
            return

        parent, child = os.path.split(path)
        if parent not in self.map or isinstance(self.map[parent].obj, Incomplete):
            if parent in self.map:
                self.map[parent].obj = []
            else:
                self.map[parent] = PathObject([], ishidden, timestamp)

            self._appendToParent(parent, self.map[parent].ishidden, timestamp)
        elif child in self.map[parent].obj:
            return

        if not ishidden:
            self.map[parent].obj.append(child)

    def _updateTimestamp(self, path, timestamp):
        timestamp = min(self.map[path].timestamp, timestamp)
        self.map[path].timestamp = timestamp
        if path != "/":
            parent, _ = os.path.split(path)
            self._updateTimestamp(parent, timestamp)

    def _append(self, path, pathobj):
        self.map[path] = pathobj
        self._appendToParent(path, pathobj.ishidden, pathobj.timestamp)
        self._updateTimestamp(path, pathobj.timestamp)

    def _fetch(self, path):
        for p, ts, ishidden, val in self.communicator.fetch(path):
            self._append(p, PathObject(val, ishidden, ts))
            if isinstance(val, str) and val not in self.map:
                self._append(val, PathObject(Incomplete(), ishidden, ts))

    def _get(self, path):
        path = path.strip()
        if len(path) > 2:
            path = path.rstrip("/")

        if path in self.map:
            obj = self.map[path].obj
            if obj is not None and not isinstance(obj, Incomplete) and not isinstance(obj, IOError):
                return self.map[path]

        cur = "/"
        prev = [""]
        for p in path.split("/"):
            cur = os.path.join(cur, p)
            if cur in self.map:
                obj = self.map[cur].obj
                if obj is None or isinstance(obj, Incomplete) or isinstance(obj, IOError):
                    self._fetch(cur)
            elif p in prev:
                self._fetch(cur)
            else:
                return None

            prev = self.map[cur].obj

        return self.map.get(path, None)

    def get(self, path):
        obj = self._get(path)
        return obj.obj if obj is not None else None

    def getwithtimestamp(self, path):
        obj = self._get(path)
        return (obj.obj, obj.timestamp) if obj is not None else (None, 0)

    def __item__(self, path):
        return self.get(path)
