# About the project

A fuse-based filesystem that get structure from the executable script.

## How to install

This application is a python package.
You can use `pip` to install it directly from github:
```sh
$ pip install https://github.com/igsha/anyfs/tarball/master
```

Another option is to use [nix](https://nixos.org/guides/install-nix.html):
```sh
$ nix profile install github:igsha/anyfs#
```

## How to use

### Mount

Like any fuse-based filesystem `anyfs` should be started as
```sh
$ anyfs /mount/point -c <cmd>
```

Parameters:
* `/mount/point` A folder where the program should mount data.

### Unmount

To unmount the mount point just use
```sh
$ fusermount -u /mount/point
```

## Protocol

`anyfs` communicates with resource via stdin and stdout.
Resource is a script or binary program that provides a directory structure.

`anyfs` sends through stdin the path to the file or directory.
The answer on stdout should be in the format `<cmd> [<count>] <path>`, where `<cmd>` is:
* `bytes` to read.
The `<count>` indicates how many bytes to read.
* `entity` is declaration of entity object: file or directory.
* `url` indicates that the next line contains URL to download the content.
The `<count>` indicates that there are additional `<count>` lines with URL header parts.
* `link` contains the redirection path.
* `notfound` means that the content is unavailable.
* `ioerror` means that there is a problem with the content.
Try again.

Special `eom` command is always indicates that there are no more messages associated with the `<path>`.

## The insides

The command `url` should contain bytes request.
The `anyfs` will try to request ranges from the URL using `Range` header and save the result in a local temporary file.
Local temporary files will be deleted after `anyfs` termination.
