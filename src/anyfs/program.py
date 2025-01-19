import fuse
from importlib.metadata import version, PackageNotFoundError
import os
import signal
import subprocess
import sys

from .anyfs import AnyFS


def main():
    try:
        __version__ = version(__package__ or __name__)
    except PackageNotFoundError:
        __version__ = "dev"

    def parselist(option, opt_str, value, parser):
        idx = len(parser.rargs)
        if "--" in parser.rargs:
            idx = parser.rargs.index("--")

        lst = parser.rargs[:idx]
        del parser.rargs[:idx]
        setattr(parser.values, "cmd", lst)

    parser = fuse.FuseOptParse(version="%prog " + __version__)
    parser.add_option("-c", "--cmd", help="Fetcher command", action="callback", callback=parselist)
    parser.add_option("-r", "--read", help="Pipe for reading commands")
    parser.add_option("-w", "--write", help="Pipe for writing paths, open it first")
    options, args = parser.parse_args()
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        return 0

    mountpoint = parser.fuse_args.mountpoint
    if mountpoint is None:
        print('Mountpoint does not exist. Cannot continue. Exiting...')
        return 1

    if not os.path.isdir(mountpoint):
        ans = input(f'Mountpoint {mountpoint} does not exist. Do you want me to create it (y/n)? ')
        if ans.lower().startswith('y'):
            os.mkdir(mountpoint)
        else:
            print('Abort...')
            return 2

    if "cmd" in options.__dir__():
        process = subprocess.Popen(options.cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=False)
        istream = process.stdout
        ostream = process.stdin
    else:
        ostream = open(options.write, "wb")
        istream = open(options.read, "rb")

    server = AnyFS(istream, ostream, fuse_args=parser.fuse_args)
    old_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
    server.main()
    signal.signal(signal.SIGINT, old_handler)
    return 0


if __name__ == '__main__':
    sys.exit(main())
