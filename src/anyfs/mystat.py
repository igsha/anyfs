import fuse
import stat


class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

    @classmethod
    def dir(clazz):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0o555
        st.n_link = 2
        return st

    @classmethod
    def file(clazz, size):
        st = MyStat()
        st.st_mode = stat.S_IFREG | 0o444
        st.st_nlink = 1
        st.st_size = size
        return st
