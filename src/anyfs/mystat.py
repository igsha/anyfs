import fuse
import os
import stat


class MyStat(fuse.Stat):
    def __init__(self, timestamp):
        super().__init__()
        self.st_nlink = 1
        self.st_uid = os.getuid()
        self.st_gid = os.getgid()
        self.st_atime = timestamp
        self.st_mtime = timestamp
        self.st_ctime = timestamp

    @classmethod
    def dir(clazz, timestamp):
        st = MyStat(timestamp)
        st.st_mode = stat.S_IFDIR | 0o555
        return st

    @classmethod
    def file(clazz, size, timestamp):
        st = MyStat(timestamp)
        st.st_mode = stat.S_IFREG | 0o444
        st.st_size = size
        return st

    @classmethod
    def link(clazz, timestamp):
        st = MyStat(timestamp)
        st.st_mode = stat.S_IFLNK | 0o555
        return st
