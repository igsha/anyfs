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
    options, args = parser.parse_args()
    mountpoint = parser.fuse_args.mountpoint
    if mountpoint is None:
        print('Mountpoint does not exist. Cannot continue. Exiting...')
        sys.exit(1)

    if not os.path.isdir(mountpoint):
        ans = input(f'Mountpoint {mountpoint} does not exist. Do you want me to create it (y/n)? ')
        if ans.lower().startswith('y'):
            os.mkdir(mountpoint)
        else:
            print('Abort...')
            sys.exit(2)

    process = subprocess.Popen(options.cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=False)
    server = AnyFS(process.stdout, process.stdin, fuse_args=parser.fuse_args)
    old_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
    server.main()
    signal.signal(signal.SIGINT, old_handler)


if __name__ == '__main__':
    main()
