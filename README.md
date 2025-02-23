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
The answer on stdout is a sequence of commands from the table below that ends with `eom` command.
There are several command that have a version with timestamp.
The timestamp is a unix timestamp.
Timestamps for the directories are the minimal timestamp value of contained files.

| Command | Description |
|---------|-------------|
| <pre>bytes &lt;count&gt; &lt;path&gt;<br>&lt;bytes&gt;</pre> | Send `<count>` `<bytes>`. |
| <pre>entity &lt;path&gt;</pre> | Forward declaration of directory of file. |
| <pre>url &lt;count&gt; &lt;path&gt;<br>&lt;url&gt;<br>&lt;Head1:value1&gt;<br>...</pre> | Send `<url>`. It can be sent `<count>` header fields. |
| <pre>link &lt;path&gt;<br>&lt;real path&gt;</pre> | Link `<real path>` by `<path>`. |
| <pre>notfound &lt;path&gt;</pre> | The requested `<path>` has not been found. |
| <pre>ioerror &lt;path&gt;</pre> | The requested `<path>` caused an I/O error. |
| <pre>eom</pre> | The special indicator to stop input command processing. |
| <pre>tbytes &lt;timestamp&gt; &lt;count&gt; &lt;path&gt;<br>&lt;bytes&gt;</pre> | `bytes` with timestamp. |
| <pre>tentity &lt;timestamp&gt; &lt;path&gt;</pre> | `entity` with timestamp. |
| <pre>turl &lt;timestamp&gt; &lt;count&gt; &lt;path&gt;<br>&lt;url&gt;<br>&lt;Head1:value1&gt;<br>...</pre> | `url` with timestamp. |
| <pre>tlink &lt;timestamp&gt; &lt;path&gt;<br>&lt;real path&gt;</pre> | `link` with timestamp. |

## The insides

The command `url` should contain bytes request.
The `anyfs` will try to request ranges from the URL using `Range` header and save the result in a local temporary file.
Local temporary files will be deleted after `anyfs` termination.
