import os


class PathMap:
    def __init__(self, protocol):
        self.protocol = protocol
        self.map = {}

    def _fetch(self, path):
        print("PathMap: fetch", path)
        for p, val in self.protocol.fetch(path):
            print("PathMap:", "write", p, val)
            self.map[p] = val

    def get(self, path):
        path = path.strip()
        if len(path) > 2:
            path = path.rstrip("/")

        if path in self.map:
            return self.map[path]

        print("PathMap: investigate", path)
        cur = "/"
        prev = [""]
        for p in path.split("/"):
            cur = os.path.join(cur, p)
            print("PathMap: investigate2", cur)
            if cur in self.map:
                print("PathMap: pass", cur)
                pass
            elif p in prev:
                print("PathMap: fetch", cur)
                self._fetch(cur)
            else:
                print("PathMap: None")
                return None

            prev = self.map[cur]

        return self.map.get(path, None)

    def __item__(self, path):
        return self.get(path)
