import argparse
import fuse
import os
import signal
import subprocess
import sys

from .anyfs import AnyFS
from . import __version__


def main():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args_parser.add_argument('-c', '--cmd', help="Command to run with args", required=True, nargs='+')
    args, unknown_args = args_parser.parse_known_args()

    parser = fuse.FuseOptParse()
    parser.parse_args(args=unknown_args)
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

    process = subprocess.Popen(args.cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=False)
    server = AnyFS(process.stdout, process.stdin)
    server.parse(args=unknown_args, errex=1)
    old_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
    server.main()
    signal.signal(signal.SIGINT, old_handler)


if __name__ == '__main__':
    main()
