import fuse
import stat


class MyStat(fuse.Stat):
    def __init__(self):
        super().__init__()
        self.st_nlink = 1

    @classmethod
    def dir(clazz):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0o555
        return st

    @classmethod
    def file(clazz, size):
        st = MyStat()
        st.st_mode = stat.S_IFREG | 0o444
        st.st_size = size
        return st

    @classmethod
    def link(clazz):
        st = MyStat()
        st.st_mode = stat.s_IFLINK | 0o555
        return st
