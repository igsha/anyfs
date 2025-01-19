#!/usr/bin/env bash
set -e

declare -A URLMAP=(\
    [file.txt]="This is file content" \
)

main() {
    while read -u $1 -r PATHARG; do
        NAMEWOSLASH="${PATHARG:1:${#PATHARG}}"
        if [[ "$PATHARG" == / ]]; then
            echo "entity /file.txt" >&$2
        elif [[ -v URLMAP[$NAMEWOSLASH] ]]; then
            LEN=$(echo "${URLMAP[$NAMEWOSLASH]}" | wc -c)
            echo "bytes $LEN $PATHARG" >&$2
            echo "${URLMAP[$NAMEWOSLASH]}" >&$2
        else
            echo "notfound $PATHARG" >&$2
        fi

        echo "eom" >&$2
    done
}

if [[ "$1" == "-i" ]]; then
    main 0 1
else
    SCRIPTDIR="$(realpath "${BASH_SOURCE[0]%/*}")"
    DIR="$(mktemp -d)"
    echo "Mount to $DIR/mnt"
    mkfifo "$DIR/pathfifo" "$DIR/cmdfifo"
    mkdir "$DIR/mnt"

    "$SCRIPTDIR/../launcher.py" "$DIR/mnt" -w "$DIR/pathfifo" -r "$DIR/cmdfifo" &
    trap "fusermount -u $DIR/mnt" INT

    exec 3< "$DIR/pathfifo"
    exec 4> "$DIR/cmdfifo"
    main 3 4
    exec 4>&-
    exec 3>&-

    rm -r "$DIR"
fi
