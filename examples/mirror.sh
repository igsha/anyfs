#!/usr/bin/env bash
set -e

DIR="$1"
while read -r PATHARG; do
    RELPATH="${DIR}${PATHARG}"
    if [[ -d "$RELPATH" ]]; then
        ENTITIES=("$RELPATH"/*)
        echo "entities ${#ENTITIES[@]}"
        printf "%s\n" "${ENTITIES[@]#$RELPATH/}"
    elif [[ -r "$RELPATH" ]]; then
        stat -c "bytes %s" "$RELPATH"
        cat "$RELPATH"
    else
        echo "notfound 0"
    fi
done
