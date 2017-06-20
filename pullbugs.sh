#!/bin/bash
desclistfile="short_desc_list.txt"
versions=(24 25 26)
statuses=("OPEN")

LONGDESC=""
while read -r line
do
    if [ -z "$LONGDESC" ]; then
        LONGDESC+="$line"
    else
        LONGDESC+=", $line"
    fi
done < "$desclistfile"

# Loop through the version and bug status list
for VER in "${versions[@]}"
do
    for STAT in "${statuses[@]}"
    do
        echo $LONGDESC
        python buggrabber.py -d "$LONGDESC" -v $VER -s $STAT
    done
done
