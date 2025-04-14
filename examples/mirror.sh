#!/usr/bin/env bash
set -e

DIR="$1"
while read -r PATHARG; do
    RELPATH="${DIR}${PATHARG}"
    if [[ -d "$RELPATH" ]]; then
        ENTITIES=("$RELPATH"/*)
        PATHARG="${PATHARG%/}"
        printf "entity path=${PATHARG}/%s\n" "${ENTITIES[@]#$RELPATH/}"
    elif [[ -r "$RELPATH" ]]; then
        RELPATH="$(readlink -f "$RELPATH")"
        stat -c "bytes size=%s time=%W path=${PATHARG}" "$RELPATH"
        cat "$RELPATH"
    else
        echo "notfound path=${PATHARG}"
    fi
    echo "eom"
done
