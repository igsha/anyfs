#!/usr/bin/env bash
set -e

declare -A URLMAP=(\
    [dragon.jpg]="https://upload.wikimedia.org/wikipedia/commons/d/d8/Friedrich-Johann-Justin-Bertuch_Mythical-Creature-Dragon_1806.jpg" \
    [kratos.jpg]="https://upload.wikimedia.org/wikipedia/commons/c/c3/Brasil_Game_Show_2014_%2815497611061%29.jpg" \
    [serotonin.svg]="https://upload.wikimedia.org/wikipedia/commons/0/04/Serotonin_%285-HT%29.svg" \
    [cow.jpg]="https://upload.wikimedia.org/wikipedia/commons/8/8c/Cow_%28Fleckvieh_breed%29_Oeschinensee_Slaunger_2009-07-07.jpg" \
)

while read -r PATHARG; do
    NAMEWOSLASH="${PATHARG:1:${#PATHARG}}"
    if [[ "$PATHARG" == / ]]; then
        echo "entities ${#URLMAP[@]} /"
        printf "%s\n" "${!URLMAP[@]}"
    elif [[ -v URLMAP[$NAMEWOSLASH] ]]; then
        echo "url $PATHARG"
        echo "${URLMAP[$NAMEWOSLASH]}"
    else
        echo "notfound $PATHARG"
    fi

    echo "eom"
done
