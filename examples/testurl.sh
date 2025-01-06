#!/usr/bin/env bash
set -e

while read -r PATHARG; do
    case "$PATHARG" in
        /)
            echo "entities 4 /"
            printf "%s\n" dragon.jpg kratos.jpg serotonin.svg cow.jpg;;
        /dragon.jpg)
            echo "url $PATHARG"
            echo "https://upload.wikimedia.org/wikipedia/commons/d/d8/Friedrich-Johann-Justin-Bertuch_Mythical-Creature-Dragon_1806.jpg";;
        /kratos.jpg)
            echo "url $PATHARG"
            echo "https://upload.wikimedia.org/wikipedia/commons/c/c3/Brasil_Game_Show_2014_%2815497611061%29.jpg";;
        /serotonin.svg)
            echo "url $PATHARG"
            echo "https://upload.wikimedia.org/wikipedia/commons/0/04/Serotonin_%285-HT%29.svg";;
        /cow.jpg)
            echo "url $PATHARG"
            echo "https://upload.wikimedia.org/wikipedia/commons/8/8c/Cow_%28Fleckvieh_breed%29_Oeschinensee_Slaunger_2009-07-07.jpg";;
        *) echo "notfound $PATHARG";;
    esac

    echo "eom"
done
